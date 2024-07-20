==========
VPS Deploy
==========

This is a base set of Fabric 2 deployment functions for projects based on
Django, Nginx, uWSGI Emperor, Memcached and PostgreSQL.

Fabric is a handy tool for automating deployment processes. Unlike Salt or
Ansible, you're writing code from the beginning rather than diving into a Turing
Tarpit of templated YAML. Also unlike Salt, Ansible or shell scripts, Fabric
neatly coordinates both local and remote SSH tasks. While Fabric may not be your
best choice for provisioning, it works well as a simple and flexible tool for
automatic custom workflows.


Installation (Fabric 2.*)
-------------------------

If Fabric 2 is available as an operating system package::

  $ sudo apt install fabric invoke
  $ pip install --user vps-deploy

Otherwise::

  $ pip install --user fabric invoke vps-deploy


Getting started
---------------

To get started, create a `fabfile.py` in your top-level project directory. It
might look something like this:

.. code:: python

   from fabric import task
   from invoke.collection import Collection

   from vps_deploy import django_fabric2 as df2

   hosts = ['user@examplehost.com']

   @task(hosts=hosts)
   def deploy(c):
       df2.transfer_files_git(c)
       df2.init(c)
       df2.grep_for_pdb(c)
       df2.lint(c)
       df2.prepare_virtualenv(c)
       df2.prepare_django(c)
       df2.fix_permissions(c,
           # Sentry needs access to Git repo.
           read=[
               '.git', 'deploy', 'env', 'project'],
           read_write=['project', 'project/collected_static/CACHE'],
       )
       df2.reload_uwsgi(c)
       df2.flush_memcached(c)
       df2.update_nginx(c)

   ns = Collection(
       deploy,
       task(df2.download_postgres_db, hosts=hosts),
       task(df2.mirror_postgres_db, hosts=hosts),
       task(df2.mirror_media, hosts=hosts),
   )
   ns.configure({
       # Built-in Fabric config.
       'run': {
           'echo': True,
           # Needed so local commands work. Can also use FABRIC_RUN_REPLACE_ENV.
           'replace_env': False,
           # Needed for Guix. Can also use FABRIC_RUN_SHELL.
           # 'shell': '/run/current-system/profile/bin/bash',
       },

       # Our custom project config.
       'env': {
           'branch': 'master',
           'app_user': 'www-data',
           'db_name': 'exampledb',
           'project_dir': '/srv/exampleproject',
           'media_dir': 'project/media',
           'virtualenv': '/srv/venvs/exampleproject-django-py38',
           'site_name': 'examplesite',
           'requirements': 'requirements/production.txt',
           'settings': 'project.settings.live',
           'uwsgi_conf': 'deploy/uwsgi.ini',
           'nginx_conf': 'deploy/nginx.conf',
           'python': '/usr/bin/python3.8',
       },
   })


Deploying
---------

To make a deployment:

`fab --prompt-for-sudo-password deploy`

This depends on a few things being already set up, such as SSH access to the
server and having the server-site software and accounts set up. Those tend to to
be better handled with configuration management tools like Salt or Ansible (and
potentially triggered by Fabric!).
