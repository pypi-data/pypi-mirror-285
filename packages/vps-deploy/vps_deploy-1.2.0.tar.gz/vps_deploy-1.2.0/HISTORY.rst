Release History
---------------

1.2.0 (2024-07-20)
++++++++++++++++++

 - only search git-tracked files in ``grep_for_pdb`` command
 - switch to f-strings throughout
 - fix conditionals failing rather than returning False
 - prevent Jinja2 from stripping trailing newlines (causes crontab issues)
 - remove setup.py (not required with Setuptools v40.0.9 under normal use and
   Pip >= 21.1 when using ``--editable``)
 - add the ability to abort deployment when local git changes present


1.1.0 (2023-07-06)
++++++++++++++++++

 - drop dependency on patchwork due to version conflict with Python
   3.11-compatible version of invoke
 - remove docs about Fabric 1


1.0.0 (2023-04-12)
++++++++++++++++++

 - remove Python 2 support
 - also look for ``breakpoint`` (Python 3.7) when checking for debugger calls
 - make ``sudo_upload_template`` function part of public API
 - use ``mktemp`` instead of deprecated ``tempfile``
 - add ``pip_install_options`` argument to ``prepare_virtualenv`` function
 - checkout ``env.branch`` before running ``git reset``


0.4.10 (2021-09-20)
+++++++++++++++++++

**Improvements**

- switch to ``setup.cfg``


0.4.9 (2021-09-20)
++++++++++++++++++

**Improvements**

- allow reading secrets from a GPG encrypted file with ``read_gpg_password_file``


0.4.8 (2021-09-18)
++++++++++++++++++

**Improvements**

 - switch to f-strings (pyupgrade --py36-plus)
 - add homepage


0.4.7 (2021-06-29)
++++++++++++++++++

**Improvements**

 - add ``transfer_files_git_pull`` command


0.4.6 (2021-06-22)
++++++++++++++++++

**Improvements**

 - Allow grep_for_pdb to accept a comma-separated string of exclusions.


0.4.5 (2021-04-29)
++++++++++++++++++

**Improvements**

 - prevent environment variables containing "%" due to uWSGI applying special
   meaning to this character
 - add ``flake8_test`` and ``mypy_test`` commands
 - switch to ``git ls-files '*.py'`` to avoid false-positives on non-versioned files


0.4.4 (2020-11-16)
++++++++++++++++++

**Bug fix**

 - don't attempt to restore database owner and privileges when running `mirror_postgres_db`


0.4.3 (2020-09-02)
++++++++++++++++++

**Bug fix**

 - fix issue ``AttributeError: Raw`` error caused by dependencies


0.4.2 (2020-08-13)
++++++++++++++++++

**Improvements**

 - use `python3 -m` to run pylint to avoid issues with Debian binary `pylint3`
   and others using just `pylint`
 - install fabric>=2.5.0 as a dependency


0.4.1 (2020-08-10)
++++++++++++++++++

**Bug fix**

 - remove workaround previously needed for Python 2 Fabric on Python 3 projects


0.4.0 (2020-08-10)
++++++++++++++++++

**Improvements**

 - add Fabric 2 equivalents of existing features


0.3.2 (2019-12-04)
++++++++++++++++++

**Improvements**

 - add optional "push_to_origin" argument to "transfer_files_git"


0.3.1 (2019-07-17)
++++++++++++++++++

**Bug fix**

 - use Python 3 compatible syntax for octal numbers


0.3.0 (2019-07-17)
++++++++++++++++++

**Improvements**

 - create a separate uWSGI config file, rather than a symbolic link, reducing
   downtime


0.2.5 (2019-01-17)
++++++++++++++++++

**Improvements**

 - Test Nginx config to make errors fail loudly
 - Added a TODO file
 - Fail deployment if Django issues a warning
 - Allow Django "check" fail level to be specified
 - Added download_postgres_db, mirror_postgres_db and mirror_media commands
 - Push the git branch configured in ``env.branch``
 - Remove install dependencies, since you probably already have Fabric 1.x installed


0.2.2 (2016-10-11)
++++++++++++++++++

 - Add README
 - Add license information
 - Remove redundant Supervisor, Bazaar and Gunicorn rules
