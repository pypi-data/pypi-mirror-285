# Copyright 2015–2023 Ben Sturmfels
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See my explainer of the problems with the built-in sudo():
# https://github.com/fabric/fabric/issues/2091#issuecomment-871071304

import datetime
import io
import os
import sys

import invoke
from jinja2 import Template


def transfer_files_git(c, push_to_origin=True, abort_on_local_changes=False):
    if push_to_origin:
        c.local(f'git push origin {c.env.branch}')
    c.sudo(f'mkdir -p {c.env.project_dir}')
    c.sudo(f'chown {c.user} {c.env.project_dir}')

    with c.cd(c.env.project_dir):
        c.run('git init --quiet')
        c.run('git config receive.denyCurrentBranch ignore')

    c.local(f"git push {c.user}@{c.host}:{c.env.project_dir} {c.env.branch}")
    with c.cd(c.env.project_dir):
        status = c.run('git status --porcelain --untracked-files=no')
        if abort_on_local_changes and status.stdout != '':
            raise invoke.Exit('Found local git changes.')
        c.run(f'git checkout --force {c.env.branch}')
        c.run(f'git reset --hard {c.env.branch} --')


def transfer_files_git_pull(c):
    """A custom transfer_files_git that pulls rather than pushes changes.

    If the repository is private, you may need some sort of token. For GitLab,
    this would be a "deploy token" deploy token in the configuration of the
    "origin" remote, eg.

    git remote add origin https://gitlab+deploy-token-XXXXXX:YYYYYYYYYYYYYYYYYYYY@gitlab.com/your-project/your-repo.git

    """
    c.sudo(f'mkdir -p {c.env.project_dir}')
    c.sudo(f'chown {c.user} {c.env.project_dir}')

    with c.cd(c.env.project_dir):
        c.run('git init --quiet')
        c.run('git config receive.denyCurrentBranch ignore')
        c.run(f'git fetch origin {c.env.branch}')
        c.run(f'git reset --hard origin/{c.env.branch}')


def init(c):
    """Misc first-time run things."""
    if not c.run(f'test -e {c.env.project_dir}/env', warn=True):
        c.run(f'touch {c.env.project_dir}/env')
    media_dir = os.path.join(c.env.project_dir, c.env.media_dir)
    if not c.run(f'test -e {media_dir}', warn=True):
        c.run(f'mkdir -p {media_dir}')


def prepare_virtualenv(c, pip_install_options=''):
    """Initialise a virtualenv and install required Python modules."""

    if not c.run(f'test -e {c.env.virtualenv}', warn=True):
        c.sudo(f"mkdir -p $(dirname {c.env.virtualenv})")
        c.sudo(f'chown {c.user} $(dirname {c.env.virtualenv})')

        c.run(f"{c.env.python} -m venv --system-site-packages {c.env.virtualenv}")
    with c.cd(c.env.project_dir):
        c.run(
            f"{c.env.virtualenv}/bin/python -m pip install -r {c.env.requirements} {pip_install_options}"
        )


def prepare_django(c, fail_level='WARNING'):
    # Clear all Python bytecode, just in case we've upgraded Python.
    c.sudo(
        f'find {c.env.project_dir} -type d -name __pycache__ -exec rm -rf {{}} +'
    )  # Python 3

    with c.cd(c.env.project_dir):
        # The `set -a` exports environment variables.
        with c.prefix(f'set -a && source {c.env.project_dir}/env'):
            # Test configuration before we attempt to restart the application server.
            fail_level_arg = ''
            if fail_level:
                fail_level_arg = f'--fail-level={fail_level}'
            c.run(
                f'{c.env.virtualenv}/bin/python manage.py check --deploy {fail_level_arg} --settings={c.env.settings}'
            )

            # Collect static files.
            c.run(
                f'{c.env.virtualenv}/bin/python manage.py collectstatic --settings={c.env.settings} -v0 --noinput'
            )

            # Migrate.
            #
            # Printing unicode characters during a migration can fail if remote
            # locale is something like "POSIX". Run `locale` to check.
            with c.prefix('LC_ALL=en_US.UTF8'):
                c.run(
                    f'{c.env.virtualenv}/bin/python manage.py migrate --settings={c.env.settings}'
                )


def fix_permissions(c, read=None, read_write=None):
    """Ensure permissions are set correctly to run site as unprivileged user."""

    if read is None:
        read = []

    if read_write is None:
        read_write = []

    # Uploading user owns the files. Web server/app user has access via group.
    # Others have no access.
    c.sudo(f'chown --recursive {c.user}:{c.env.app_user} {c.env.project_dir}')
    c.sudo(f'chmod --recursive u=rwX,g=,o= {c.env.project_dir}')

    # Assume we always need read access to project directory.
    c.sudo(f'chmod g+rX {c.env.project_dir}')

    for path in read:
        c.sudo(f'chmod --recursive g+rX {os.path.join(c.env.project_dir, path)}')
    for path in read_write:
        c.sudo(f'chmod --recursive g+rwX {os.path.join(c.env.project_dir, path)}')


def sudo_upload_template(c, local_path, remote_path, mode, owner=None, group=None):
    # My hacked up replacement for upload template is permanently sudo and uses
    # full Jinja2 by default (both unlike Fabric 1).
    owner = c.user if owner is None else owner
    group = c.user if group is None else group
    with open(local_path) as f:
        content = f.read()
    # Jinja2 will strip the trailing newline by default, which causes
    # crontab-style files to be rejected.
    t = Template(content, keep_trailing_newline=True)
    output = t.render(env=c.env, **c.env)  # Both env.X and just X.
    m = io.StringIO(output)
    c.put(m, '/tmp/X')
    c.sudo(f'mv /tmp/X {remote_path}')
    c.sudo(f'chown {owner}:{group} {remote_path}')
    c.sudo(f'chmod {mode} {remote_path}')


# Backwards compatibility support for this now public function
_sudo_upload_template = sudo_upload_template


def reload_uwsgi(c):
    sudo_upload_template(
        c, c.env.uwsgi_conf, f'/etc/uwsgi-emperor/vassals/{c.env.site_name}.ini', '644'
    )

    # Append secrets to uWSGI config on-the-fly.
    #
    # uWSGI config format for environment variables is different to a file
    # you might `source`. It has "env = " at the start instead of export,
    # doesn't mind whitespace in the values and treats quotes literally.
    #
    # See here on getting quotes right in Fabric
    # https://lists.gnu.org/archive/html/fab-user/2013-01/msg00005.html.

    # Don't use percent characters in environment variables because uWSGI will
    # silently drop them unless they are doubled-up (meaning that you'll have a
    # hard time tracking down the subtle bug).
    try:
        c.run(f"! grep '%' {c.env.project_dir}/env")
    except invoke.exceptions.UnexpectedExit:
        print(
            'Environment variables should not contain "%" due to its special use in uWSGI config.',
            file=sys.stderr,
        )
        raise

    # Removes quotes as these are interpreted literally by uWSGI.
    c.sudo(f'echo "" >> /etc/uwsgi-emperor/vassals/{c.env.site_name}.ini')
    c.sudo(
        f"""sed 's/export//' {c.env.project_dir}/env | sed 's/^/env =/' | sed "s/['\\"]//g" >> /etc/uwsgi-emperor/vassals/{c.env.site_name}.ini"""
    )


def flush_memcached(c):
    """Clear cache by restarting the memcached server.

    By design, any user on the system can issue commands to memcached, including
    to flush the whole cache. Alternately, we could install libmemcached-tools
    and run `memcflush --servers localhost`.

    """
    c.run("echo flush_all | nc -w1 localhost 11211")


def update_nginx(c):
    sudo_upload_template(
        c, c.env.nginx_conf, f'/etc/nginx/sites-available/{c.env.site_name}', '644'
    )
    c.sudo(
        f"ln -s --force /etc/nginx/sites-available/{c.env.site_name} /etc/nginx/sites-enabled/{c.env.site_name}"
    )
    c.sudo("/usr/sbin/nginx -t")
    c.sudo("/etc/init.d/nginx force-reload")


def download_postgres_db(c):
    tempfile = c.run('mktemp').stdout.strip()
    c.sudo(f'pg_dump --format=c {c.env.db_name} > {tempfile}', user='postgres', pty=True)
    localtempfile = '{env.site_name}-{time:%Y-%m-%dT%H:%M:%S}.dump'.format(
        env=c.env, time=datetime.datetime.now()
    )
    c.get(tempfile, localtempfile)
    # localtempfile = get(tempfile, local_path='%(basename)s')[0]
    c.sudo(f'rm -f {tempfile}')
    return localtempfile


def mirror_postgres_db(c):
    localtempfile = download_postgres_db(c)
    c.local(f'dropdb --if-exists {c.env.db_name}')
    c.local(f'createdb {c.env.db_name}')

    # Using sudo here avoids permission errors relating to extensions.
    #
    # Tried removing the above drop and create and adding --clean --create
    # below, but I get a whole bunch of errors relating to things already being
    # in the database.
    c.local(
        f'pg_restore --no-owner --no-privileges --dbname={c.env.db_name} {localtempfile}',
        warn=True,
    )

    c.local(
        f"""psql {c.env.db_name} -c "update django_site set domain = '127.0.0.1:8000'" """,
        warn=True,
    )
    print(
        'You may want to run:\npython3 -m django createsuperuser --username=admin --email=sysadmin@sturm.com.au'
    )


def mirror_media(c):
    c.local(
        f'rsync -avz {c.user}@{c.host}:{c.env.project_dir}/{c.env.media_dir}/ {c.env.media_dir}'
    )


def lint(c):
    """Run Pylint over everything."""

    # --jobs=0 enable parallelism based on number of cores available.
    c.local("git ls-files '*.py' | xargs python3 -m pylint --jobs=0 --rcfile=pylint.conf")


def flake8_test(c):
    # See .flake8 for excluded checks.
    c.local("git ls-files '*.py' | xargs python3 -m flake8")


def mypy_test(c):
    c.local("git ls-files '*.py' | xargs python3 -m mypy --config-file mypy.ini")


def grep_for_pdb(c):
    """Check that code doesn't ever call the debugger.

    Doing so in production would lock up worker processes.

    """
    c.local(
        r"! git ls-files '*.py' ':!:fabfile.py' | xargs grep -n '\b\(pdb\|breakpoint\)\b'"
    )


def django_test(c):
    c.local('python3 manage.py test --keepdb')


def check_site_online(c):
    """Perform a basic check so we know immediately if the website is down."""

    # TODO: Is there a better way to make invoke fail loudly?
    try:
        c.run(f'curl --silent --head {c.env.url} | grep --perl-regexp "^HTTP/.+ 200"')
    except invoke.UnexpectedExit:
        raise invoke.Exit('Site check failed!')


def install_scheduled_jobs(c, periodic_jobs=None, crontabs=None):
    periodic_jobs = [] if periodic_jobs is None else periodic_jobs
    crontabs = [] if crontabs is None else crontabs

    typical_periodic_jobs = {
        'cron.hourly',
        'cron.daily',
        'cron.weekly',
        'cron.monthly',
    }
    for job in periodic_jobs:
        basename = os.path.basename(job)
        if basename in typical_periodic_jobs:
            sudo_upload_template(
                c,
                job,
                f'/etc/{basename}/{c.env.site_name}',
                '755',
            )
        else:
            raise RuntimeError(f'Unexpected periodic job: {job}')
    for crontab in crontabs:
        name = os.path.basename(crontab).replace('cron.', '')
        sudo_upload_template(
            c,
            crontab,
            f'/etc/cron.d/{c.env.site_name}-{name}',
            '644',
            'root',
            'root',
        )


def django_shell(c):
    with c.cd(c.env.project_dir):
        c.run(
            f'set -a && source ./env && DJANGO_SETTINGS_MODULE={c.env.settings} {c.env.virtualenv}/bin/python manage.py shell',
            pty=True,
        )


def bash(c):
    with c.cd(c.env.project_dir):
        c.run('bash', pty=True)


def read_gpg_password_file(c, path):
    """Store your secrets in a GPG encrypted file.

    Then in your deploy command task, you can do:

    if not c.config.sudo.password:
        c.config.sudo.password = read_gpg_password_file(c, 'some-file.gpg')

    """
    result = c.local(f'gpg --quiet -d {path}', hide=True)
    return result.stdout.strip()
