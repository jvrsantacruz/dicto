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
* Simple to *extend* adding custom `Jinja2 <http://jinja.pocoo.org>`_
  templates, and extra remote resources remote resources as *plugins*.
* Offering a very straight-forward command line interface for humans.


Commands
--------

dicto view
~~~~~~~~~~

*dicto view* renders templates to the standard output using external data:

::

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

The next example will show a use case for generating a changelog using external
info from a Redmine resource:

1. Define a template using available Redmine info along with some basic template
vars (*current_date*) and some user defined ones (*codename*):

::

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

::

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

Dicto shell
~~~~~~~~~~~

*dicto shell* fetches all context data needed for template rendering and opens
a interactive shell having those variables available for direct use,
exploration and experimentation.

::

    dicto shell --profile dua
    Enter redmine password:
    Enter redmine version: v10.17.1
      __/   .  __  -/- _,_
    _(_/(__/__(_,__/__(_/

    Template rendering interactive context.

    Available vars:
     profile, apt_url, template, redmine_project, redmine_user, redmine_issues,
     current_date, redmine, redmine_url, file, apt_packages, redmine_api, data,
     redmine_version

    In [1]: redmine_version.
    redmine_version.container_all     redmine_version.post_create       redmine_version.redmine_version
    redmine_version.container_create  redmine_version.post_update       redmine_version.refresh
    redmine_version.container_filter  redmine_version.pre_create        redmine_version.requirements
    redmine_version.container_one     redmine_version.pre_update        redmine_version.save
    redmine_version.container_update  redmine_version.project           redmine_version.sharing
    redmine_version.created_on        redmine_version.query_all         redmine_version.status
    redmine_version.description       redmine_version.query_create      redmine_version.translate_params
    redmine_version.id                redmine_version.query_delete      redmine_version.updated_on
    redmine_version.internal_id       redmine_version.query_filter      redmine_version.url
    redmine_version.is_new            redmine_version.query_one
    redmine_version.name              redmine_version.query_update


If available, the ``ipython`` package will be used, for a much nicer
experience over the standard python shell. To install ``ipython`` use: ``pip
install ipython``.

Configuration
-------------

All accepted command line arguments and options can be set in the
configuration file to avoid typing they again. In the file, keys and values
under the ``default`` key will be used as command line arguments.

This configuration file would allow to run the changelog example without
arguments:

::

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

::

    profiles:
        email:
            redmine: true
            redmine_user: jsl
            template: email.tpl.html

They can be referenced and applied from the command line using the
``--profile NAME`` option.


::

    dicto view --profile email


Default locations
~~~~~~~~~~~~~~~~~

The configuration can be specified to dicto from the command line:

::

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
``config.yaml`` file; the ``profile`` section of the same file, can define the
option again and override it. The program will take the value from the config
file unless it gets defined first in an environment variable. The user can
always override all of the previous values by setting the option in the
command line, which takes precedence over all the rest.

All the different ways of defining the same option, more important first:

1. command line argument (`--template`)
2. environment variable (`dicto_TEMPLATE`)
3. `profile` config file section
4. `default` config file section

Resources
---------

The tool bundles in several default data resources. Each of them tries to
obtain as much information as possible from a resource and make it available
in the context of user defined templates.

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
  and ``size`` sorted by version (*name*).

Other resources
~~~~~~~~~~~~~~~

The user can add extra data using the ``--data key:value`` and ``--file
key:path`` options. Using those options, one or many variables can be set in
the template context. ``--data`` will add the literal value as given in the
command line. ``--file`` will open the given *path* read a file and put its
contents in the variable.  In case of reusing a *key*, ``--data`` prevails
over ``--file``.

eg:

::

    dicto view --data author:jsl \
               --data env:production \
               --file version:version.txt \
               --template mytemplate.tpl.txt

The previous command would add the ``author``, ``env`` and ``version`` to
``mytemplate.tpl.txt`` rendering context and so they can be used within the
template.

Templates
---------

All output can be personalized by the user using custom `Jinja2
<http://jinja.pocoo.org>`_ template files. See the `template designer
documentation <http://jinja.pocoo.org/docs/dev/templates/>`_ for more
information about the available syntax and functions.


Usage
-----

Base command:

::

    Usage: dicto [OPTIONS] COMMAND [ARGS]...

    Options:
    --version      Show the version and exit.
    -v, --verbose  Level of verbosity  [default: 0]
    --config PATH  Path to the config.yaml file envvar: DICTO_CONFIG
    --help         Show this message and exit.

    Commands:
    view

Common options for ``view`` and ``shell``:

::

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
    --file TEXT               Extra data from a text file in key:path format.
                                Reads the whole file. Can be used multiple times
    --help                    Show this message and exit.


Installation
------------

Install dependencies within a virtualenv and then the application itself.

::

    virtualenv env
    source env/activate
    pip install .

Or from our *pypiserver*:

::

    $ pip install dicto
