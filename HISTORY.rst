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
