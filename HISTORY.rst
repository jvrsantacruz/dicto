0.8.1 (2016-01-14)
------------------

* Fixes testing environments
* Fixes problem with hg tags text encoding

0.8.0 (2015-09-10)
------------------

* Adds --redmine-key option for Redmine token authentication

0.7.1 (2015-09-03)
------------------

* Fixes default tag for git, searches for master ref

0.7.0 (2015-09-02)
------------------

* Fixes git warning that goes 'could not use master, using master'
* Fixes broken output of --exe strings assuming input is utf-8 text
* Fixes error with git_version_commits
* Fixes problem with empty configuration files
* Adds dicto context command that prints current context to stdout
* Adds  variable and fixes default location issues

0.6.0 (2015-08-27)
------------------

* Fixes git tag detection to match mercurial's behaviour
* Fixes problem with empty configuration files
* Adds dicto context command that prints current context to stdout
* Fixes fixes default location issues and adds $DICTO_HOME env variable

0.5.0 (2015-08-26)
------------------

* Adds git support

0.4.0 (2015-08-21)
------------------

* Changes --exe to allow shell commands such as 'ls | grep name'
* Changes arg handling to consider --data/--exe as input arguments

0.3.0 (2015-08-19)
------------------

* Fixes config file loading to allow empty config files
* Adds --exe option which gets external program output
* Adds default config location at $(pwd)/.dicto/config.yaml

0.2.1 (2015-08-19)
------------------

* Fixes package versions for testing
* Adds firsts tests
* Adds MANIFEST.in to package version files
* Adds python3 support
* Changes unicode_literal in favour of u'' strings

0.2.0 (2015-08-06)
------------------

* Adds --output option to write contents to a file
* Adds --append option to append contents to a file
* Adds --prepend option to prepend contents to an existing file

0.1.0 (2015-07-07)
------------------

* First version
* Jinja2 templates
* Redmine integration support
* Mercurial integration support
* Chef integration support
* Apt integration support
