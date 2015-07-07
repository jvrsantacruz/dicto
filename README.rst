Dicto
*****


Integrated, configurable and extensible automated text template processor for
notification generation.

* Provides access to a wide range of remote resources offering interesting
  domain, management and infrastructure information, through *integrations*
  with several external applications such as *redmine*, *mercurial*, *chef*,
  *apt* or even arbitrary user-defined data.
* *Configurable* through `yaml <http://www.yaml.org>`_ files,
  defining a *profile* based system, allowing for multiple complex
  configurations to be easily used, shared and extended.
* Simple to *extend* adding custom `Jinja2 <http://jinja.pocoo.org>`
  templates, and extra remote resources remote resources as *plugins*.
* Offering a very straight-forward command line interface for humans.

.. code:: shell

    dicto view --profile duataric_email

    Hemos cerrado en pruebas duasql v10.16.9

    | Proyecto      |  duasql |
    |-------------- | ----------------|
    | Versión       | v10.16.9  |
    | Fecha         | 2015-07-06 |
    | Planificación | [redmine/versions/v10.16.9](http://redmine.taric.local/versions/1244) |
    | Documentación | [docs.taric.local/docs/duasql/v10.16.9](http://docs.taric.local/docs/duasql/v10.16.9) |

    Los cambios incluyen:

    * **Errores** ([#15432](http://http://redmine.taric.local/issues/15432)) Mensaje de discrepancia para duas edi export y Transito

Use case of generating a changelog using info from Redmine:

1. Define a template using available Redmine info along with some basic template
vars (*current_date*) and some user defined ones (*codename*):

.. code:: rst

    (./changelog.tpl.rst)

    .. changelog::
        :version: {{redmine_version.name}}
        :released: {{current_date.date()}}

        `{{codename}} <{redmine_version.url}>`_

        {{redmine_version.description}}

        Changes:

        {% for issue in redmine_issues %}
            .. change::
            :tags: {{issue.tracker.name|lower}}
            :tickets: {{issue.id}}

            {{issue.subject}}
        {% endfor %}

2. Generate the result, accessing Redmine using user credentials:

.. code:: shell

    dicto view --redmine\
                 --redmine-url http://redmine.taric.local\
                 --redmine-version v10.16.9 \
                 --redmine-project duataric \
                 --template changelog.tpl.rst \
                 --data codename:Zarzaparrilla
    Enter redmine user: jsl
    Enter redmine password:

    .. changelog::
        :version: v10.16.9
        :released: 2015-07-06

        `Zarzaparrilla  <{redmine_version.url}>`_

        Bugfixing release

        Changes:

            .. change::
            :tags: errores
            :tickets: 15432

            Mensaje de discrepancia para duas edi export y Transito

Configuration
-------------

All accepted command line arguments and options can be set in the
configuration file to avoid typing they again. In the file, keys and values
under the ``default`` key will be used as command line arguments.

This configuration file would allow to run the changelog example without
arguments:

.. code:: yaml

    default:
        redmine: true
        redmine_user: jsl
        redmine_url: http://redmine.taric.local
        redmine_version: v10.16.9
        template: changelog.tpl.rst
        data:
            codename: Zarzaparrilla


Profiles
~~~~~~~~

Profiles are named groups of options that can be reused. They can be defined
as groups of key, value options under a name within the ``profiles`` section.

.. code:: yaml

    profiles:
        email:
            redmine: true
            redmine_user: jsl
            template: email.tpl.html

They can be referenced and applied from the command line using the
``--profile NAME`` option.


.. code:: shell

    dicto view --profile email


Default locations
~~~~~~~~~~~~~~~~~

The configuration can be specified to dicto from the command line:

.. code:: shell

    dicto --config /pat/to/cfg.yaml view (..)

from an environment variable: ::

    export DICTO_CONFIG=/path/to/cfg.yaml

or it is read from several default locations; dicto searches for a
configuration file in the following places in order:

* ``./.dicto.yaml``: A file named ``.dicto.yaml`` in the current
  directory.
* ``~/.dicto/config.yaml``: A file named ``config.yaml`` in the *dicto*
  user directory.

The ``~`` character refers to user's ``$HOME`` in Linux and Mac OS X, see the
`possible locations <http://click.pocoo.org/4/api/#click.get_app_dir>`_ for
Windows.


Overriding arguments:
~~~~~~~~~~~~~~~~~~~~~

Command line arguments might be set in the ``default`` section of the
``config.yaml`` file, the ``profile`` section of the same file, can define the
option again and override it, the program will take that value unless is
defined in an environment variable, which goes first, the but it can be later
specified again at the command line, which takes precedence over all the rest.

All the different ways of defining the same option, more important first:

1. command line argument (`--template`)
2. environment variable (`dicto_TEMPLATE`)
3. `profile` config file section
4. `default` config file section

Resources
---------

The tool comes with several default data resources. Each of them tries to
obtain certain information from a resource and make it available from the user
defined templates.

Redmine
~~~~~~~

Fetches project, version and all closed issues from a given Redmine project
version.
The following variables are available to use within the template:

* ``redmine_api``: api object with general Redmine data.
* ``redmine_project``: project object with the specified Redmine project data.
* ``redmine_version``: version object with the specified Redmine version data.
* ``redmine_issues``: List of issue objects with the list of open issues
  in the *project* at given *version*.

Datatypes:

* ``project``: See `project object <http://python-redmine.readthedocs.org/resources/project.html>`_ documentation.
* ``version``: See `version object <http://python-redmine.readthedocs.org/resources/version.html>`_ documentation.
* ``issue``: See `issue object <http://python-redmine.readthedocs.org/resources/issue.html>`_ documentation.

See also:

* `Object reference <http://python-redmine.readthedocs.org/resources/issue.html>`_
* `Rest API reference <http://www.redmine.org/projects/redmine/wiki/Rest_api>`_

Mercurial
~~~~~~~~~

Fetches all repository info, commits, tags and commits within a *version*.
The following variables are available to use within the template:

* ``hg_repo``: api object with general mercurial info and operations.
* ``hg_tags``: List of all tags objects in the repository.
* ``hg_commits``: List of all commits within the repository in log order.
* ``hg_version_tag``: Tag object specified in *hg_version*.
* ``hg_version_commits``: List of all commits between the tag in *hg_version*
  and the previous one (if any).

Datatypes:

* ``tag``: namedtuple ``(name, rev, node, islocal)``
* ``commit``: namedtuple ``rev, node, tags (space delimited), branch, author, desc, datetime``

See also:

* `python-hglib <https://mercurial.selenic.com/wiki/PythonHglib>`_
* `python-hglib client code <https://selenic.com/repo/python-hglib/file/ec935041d1ff/hglib/__init__.py>`_

Chef
~~~~

Fetches chef repository info about environments and nodes.
The following variables are available to use within the template:

* ``chef_envs``: dict of environments by name.
* ``chef_nodes``: dict of nodes by name.

Datatypes:

* ``Environment``: `See `environment object
  <http://pychef.readthedocs.org/en/latest/api.html#environments>`_ in the
  chef plugin documentation. Each env has a ``name`` attribute, ``attributes`` dict, ``override_attributes`` dict.
* ``Node``: `See `node object
  <http://pychef.readthedocs.org/en/latest/api.html#nodes>`_ in the chef
  plugin documentation. Each node has ``name``, ``chef_environment``,
  ``run_list`` and ``attributes``, ``override`` dict, ``default`` dict,
  ``automatic`` dict.

See also:

* `PyChef <http://pychef.readthedocs.org/en/latest>`_ documentation.
* `Chef REST Api <https://docs.chef.io/api_chef_server.html>`_ documentation.

Apt
~~~

Fetches package names and urls from an aptitude repository for some packages.
The following variables are available to use within the template:

* ``apt_packages``: dict by name of of dicts with data for each package.

Datatypes:

* ``apt_packages``: Each dict contains ``name``, ``url`` and a ``versions``
  list. The ``versions`` list contains dicts with ``name``, ``url``, ``date``
  and ``size``

The *version* list of available packages is version sorted asc.

Other resources
~~~~~~~~~~~~~~~

The user can add extra data using the ``--data key:value`` and ``--file
key:path`` options. Using those options, one or many variables can be set in
the template. ``--data`` will add the literal value as given in the command
line. ``--file`` will read the given *path* and put its contents in the
variable.  In case of reusing a *key*, ``--data`` prevails over ``--file``.

.. code:: shell

    dicto view --data author:jsl \
               --data env:production \
               --file version:version.txt \
               --template mytemplate.tpl.txt

The previous command would add the ``author``, ``env`` and ``version`` to
``mytemplate.tpl.txt`` rendering context and so they can be used within the
template.


Usage
-----

Base command:

.. code::

    Usage: dicto [OPTIONS] COMMAND [ARGS]...

    Options:
    --version      Show the version and exit.
    -v, --verbose  Level of verbosity  [default: 0]
    --config PATH  Path to the config.yaml file envvar: DICTO_CONFIG
    --help         Show this message and exit.

    Commands:
    view

View command:

Usage: dicto view [OPTIONS]

    Options:
    --chef / --no-chef        enable/disable chef resource (default: false)
    --apt / --no-apt          enable/disable apt resource (default: false)
    --apt-url TEXT            apt repository base url envvar: APT_URL
    --apt-packages TEXT       apt packages to include.
    --hg / --no-hg            enable/disable mercurial resource (default: false)
    --hg-repo TEXT            mercurial repository PATH/URL envvar: HG_REPO
    --hg-version TEXT         mercurial add tag to the data evvar: HG_VERSION
    --redmine / --no-redmine  enable/disable redmine resource (default: false)
    --redmine-url TEXT        redmine application base url envvar: REDMINE_URL
    --redmine-user TEXT       redmine username envvar: REDMINE_USER
    --redmine-project TEXT    redmine project slug evvar: REDMINE_PROJECT
    --redmine-version TEXT    redmine project version envvar: REDMINE_VERSION
    --redmine-password TEXT   redmine user's password envvar: REDMINE_PASSWORD
    --data TEXT               Extra data in key:value format. Can be used
                                multiple times.
    --template PATH           Path to a Jinja2 template.
    --profile TEXT            Name of an existing profile in config to load
                                options from.
    --help                    Show this message and exit.


Installation
------------

Install dependencies within a virtualenv and then the application itself.

.. code:: shell

    virtualenv env
    source env/activate
    pip install .

Or from our *pypiserver*:

.. code:: shell

    $ pip install dicto
