from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import re
import ssl
import shutil
import urllib2
import inspect
import tempfile
import datetime
import functools
import contextlib
import collections

import chef
import yaml
import click
import hglib
import jinja2
import natsort
import redmine
import requests

DEFAULT_CONFIG_PATHS = [
    os.path.join(os.getcwd(), '.dicto.yaml'),
    os.path.join(click.get_app_dir('dicto', force_posix=True), 'config.yaml')
]


def _parse_option_config(ctx, param, value):
    if not value:
        # search for the most specific default config file
        for path in DEFAULT_CONFIG_PATHS:
            path = os.path.abspath(path)
            if os.path.isfile(path):
                return path

    return value


def manage_errors(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            error(unicode(e))

    return decorator


@click.group()
@manage_errors
@click.pass_context
@click.version_option()
@click.option('-v', '--verbose', count=True,
              help="Level of verbosity", show_default=True)
@click.option('--config', callback=_parse_option_config, envvar='DICTO_CONFIG',
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              help='Path to the config.yaml file envvar: DICTO_CONFIG')
def cli(ctx, verbose, config):
    ctx.obj = {}

    ctx.obj['verbose'] = max(0, min(2, verbose))
    echo(ctx.obj, 'Reading config file from: {}'.format(config), level='verbose')

    ctx.obj['config_path'] = config
    ctx.obj['config'] = read_config(config) if config else {}
    echo(ctx.obj, 'Configuration:\n {!r}'.format(ctx.obj['config']), level='debug')


def _parse_option_list(value):
    return dict(entry.split(':', 1) for entry in value or [])


def _parse_option_data(ctx, param, value):
    try:
        return _parse_option_list(value)
    except ValueError:
        raise Error(u'--data Option must keep a key:value format')


def _parse_option_file(ctx, param, value):
    try:
        value = _parse_option_list(value)
        # open and read all files
        for name in value:
            path = os.path.abspath(value[name])
            with io.open(path, encoding='utf-8') as stream:
                value[name] = stream.read().strip()
        return value
    except ValueError:
        raise Error(u'--file Option must keep a key:path format')


def _parse_option_apt_packages(ctx, param, value):
    if not value:
        return []
    return value


def common_data_options(function):

    options = [
        click.option('--chef/--no-chef', is_flag=True, default=None,
                     help="enable/disable chef resource (default: false)"),
        click.option('--apt/--no-apt', is_flag=True, default=None,
                     help="enable/disable apt resource (default: false)"),
        click.option('--apt-url', envvar='APT_URL',
                     help="apt repository base url envvar: APT_URL"),
        click.option('--apt-packages', multiple=True, callback=_parse_option_apt_packages,
                     help="apt packages to include."),
        click.option('--hg/--no-hg', is_flag=True, default=None,
                     help="enable/disable mercurial resource (default: false)"),
        click.option('--hg-repo', envvar='HG_REPO',
                     help="mercurial repository PATH/URL envvar: HG_REPO"),
        click.option('--hg-version', envvar='HG_VERSION',
                     help="mercurial add tag to the data evvar: HG_VERSION"),
        click.option('--redmine/--no-redmine', is_flag=True, default=None,
                     help="enable/disable redmine resource (default: false)"),
        click.option('--redmine-url', envvar='REDMINE_URL',
                     help="redmine application base url envvar: REDMINE_URL"),
        click.option('--redmine-user', envvar='REDMINE_USER',
                     help="redmine username envvar: REDMINE_USER"),
        click.option('--redmine-project', envvar='REDMINE_PROJECT',
                     help="redmine project slug evvar: REDMINE_PROJECT"),
        click.option('--redmine-version', envvar='REDMINE_VERSION',
                     help="redmine project version envvar: REDMINE_VERSION"),
        click.option('--redmine-password', envvar='REDMINE_PASSWORD',
                     help="redmine user's password envvar: REDMINE_PASSWORD"),
        click.option('--data', callback=_parse_option_data, multiple=True,
                     help="Extra data in key:value format. Can be used multiple times."),
        click.option('--template', type=click.Path(exists=True, dir_okay=False, resolve_path=True),
                     envvar='DICTO_TEMPLATE', help="Path to a Jinja2 template."),
        click.option('--profile', envvar='DICTO_PROFILE',
                     help="Name of an existing profile in config to load options from."),
        click.option('--file', multiple=True, callback=_parse_option_file,
                     help="Extra data from a text file in key:path format. "
                     "Reads the whole file. Can be used multiple times")
    ]

    for option in options:
        function = option(function)

    return function


@cli.command()
@manage_errors
@click.pass_obj
@common_data_options
def view(obj, **kwargs):
    kwargs = resolve_args(obj['config'], kwargs)

    echo(obj, 'Connecting to remote resources', level='verbose')
    context = make_context(kwargs)
    echo(obj, 'Render context:\n {!r}'.format(context), level='debug')

    template = kwargs.get('template') or error('No template given')
    click.echo(render_template(template, context))


@cli.command()
@manage_errors
@click.pass_obj
@common_data_options
def shell(obj, **kwargs):
    kwargs = resolve_args(obj['config'], kwargs)
    context = make_context(kwargs)
    make_shell(obj, context)


def make_context(kwargs):
    """Builds template context from all data resources"""
    context = dict(current_date=datetime.datetime.now())
    context.update(kwargs)
    context.update(kwargs['file'])
    context.update(kwargs['data'])

    if kwargs.get('redmine'):
        context.update(get_redmine_data(only_args_with('redmine_', kwargs)))

    if kwargs.get('hg'):
        context.update(get_hg_data(only_args_with('hg_', kwargs)))

    if kwargs.get('chef'):
        context.update(get_chef_data())

    if kwargs.get('apt'):
        context.update(get_apt_data(only_args_with('apt_', kwargs)))

    if 'redmine_password' in context:
        del context['redmine_password']  # do not print this

    return context


def resolve_args(config, kwargs):
    """Get given argument values using preference: cli/profile/config"""
    # get arguments from config file
    resolved_kwargs = config.get('default', {})

    # override with profile arguments if any
    profile = get_profile(config, kwargs.get('profile'))
    recursively_update(resolved_kwargs, profile)

    # override with given cli arguments
    recursively_update(resolved_kwargs,
        {key: value for key, value in kwargs.items() if value is not None})

    return resolved_kwargs


def recursively_update(data, update):
    """Adds up nested dict values"""
    for key, update_value in update.items():
        data_value = data.get(key)
        if isinstance(data_value, dict) and isinstance(update_value, dict):
            recursively_update(data_value, update_value)
            data_value.update(update_value)
        elif isinstance(data_value, list) and isinstance(update_value, list):
            data_value.extend(update_value)
        else:
            data[key] = update_value


def only_args_with(prefix, kwargs):
    return {k: v for k, v in kwargs.items() if k.startswith(prefix)}


def get_profile(config, profile_name):
    profiles = config.get('profiles', {})

    if not profile_name:
        return {}

    if profile_name and not profiles:
        error('No profiles configured')

    if profile_name not in profiles:
        error('Profile "{}" do not exists.\nShould be one of:\n {}'.format(
            profile_name, '\n '.join(profiles.keys())))

    return profiles[profile_name]


def read_config(path):
    context = dict(
        config=path,
        config_dir=os.path.dirname(path)
    )

    return yaml.load(render_template(path, context))


def prompt_for_missing_values(kwargs, required=None):
    required = required if required else kwargs.keys()

    for key in required:
        if kwargs.get(key) is None:
            kwargs[key] = click.prompt(
                text='Enter ' + key.replace('_', ' '),
                hide_input='password' in key
            )


def get_redmine_data(kwargs):
    required = get_function_args(fetch_redmine_data)
    prompt_for_missing_values(kwargs, required)
    return fetch_redmine_data(**kwargs)


def get_project_by_name(redmine, project_name):
    return first(p for p in redmine.project.all()
                 if p.name.lower() == project_name.lower())


def get_version_by_name(project, version_name):
    return first(v for v in project.versions if v.name == version_name)


def fetch_redmine_data(redmine_url, redmine_user, redmine_password, redmine_project, redmine_version):
    """Return a dict of redmine data resources

      redmine_api: Object for redmine at *redmine_url*
      redmine_project: Object for *redmine_project* at *redmine_url*
      redmine_version: Object for *redmine_version* at *redmine_project*
      redmine_issues: List of objects for open issues in *redmine_project*
       at *redmine_version*
    """
    api = redmine.Redmine(redmine_url, username=redmine_user, password=redmine_password)

    project = get_project_by_name(api, redmine_project)
    if project is None:
        error('redmine: Project "{}" not found'.format(redmine_project))

    version = get_version_by_name(project, redmine_version)
    if version is None:
        error('redmine: Project "{}" has no version "{}"'
              .format(redmine_project, redmine_version))

    issues = api.issue.filter(
        project_id=project.id,
        fixed_version_id=version.id,
        status_id='closed'
    )

    return dict(
        redmine_api=api,
        redmine_issues=issues,
        redmine_project=project,
        redmine_version=version
    )


def render_template(path, context):
    try:
        return make_template(path).render(context)
    except jinja2.TemplateError as e:
        error(unicode(e) + ' in template ' + click.format_filename(path))


def make_template(path):
    with io.open(os.path.abspath(path), 'r', encoding='utf-8') as stream:
        return jinja2.Template(stream.read())


def get_hg_data(hg_config):
    required = get_function_args(fetch_hg_data)
    prompt_for_missing_values(hg_config, required)
    return fetch_hg_data(**hg_config)


hg_tag = collections.namedtuple('Tag', ['name', 'rev', 'node', 'islocal'])


@contextlib.contextmanager
def hg_tmp_clone(hg_repo):
    """Clone repository in a temporary path"""
    try:
        hg_tmp_path = ''
        hg_repo_path = hg_repo

        # clone remote repositories into a temporal directory
        if hg_repo.startswith('http') or hg_repo.startswith('ssh'):
            hg_tmp_path = hg_repo_path = tempfile.mkdtemp(prefix='dicto-hg')
            try:
                hglib.clone(hg_repo, hg_repo_path)
            except hglib.error.ServerError as e:
                error('hg: could not clone {} into {}: {}'
                      .format(hg_repo, hg_tmp_path, unicode(e)))

        yield hg_repo_path
    finally:
        # remove temporal path if created
        if os.path.isdir(hg_tmp_path):
            shutil.rmtree(hg_tmp_path)


@contextlib.contextmanager
def hg_open_or_clone_repo(hg_repo):
    """Open local repo. Clone when non local path is given"""
    with hg_tmp_clone(hg_repo) as hg_repo_path:
        try:
            yield hglib.open(hg_repo_path)
        except hglib.error.ServerError as e:
            error('hg: {} could not open {}'.format(e, hg_repo))


def hg_version_objects(repo, tags, hg_repo, hg_version):
    """Gets objects related to tag as a 'version'"""
    version_tag = first(t for t in tags if t.name == hg_version)
    if version_tag is None:
        error('hg: No tag named "{}" in {}'.format(hg_version, hg_repo))

    try:
        prev_version_tag = tags[tags.index(version_tag) + 1]
    except IndexError:
        revspec = version_tag.name
    else:
        revspec = version_tag.name + ':' + prev_version_tag.name

    version_commits = repo.log(revspec)
    if not version_commits:
        echo('hg: No commits for version {} in {}'
            .format(revspec, hg_repo), intend='warning')

    return version_tag, version_commits


def fetch_hg_data(hg_repo, hg_version):
    """Return a dict with mercurial repo data resources

      hg_repo: Object for *hg_repo* mercurial repository
      hg_tags: List of all tag objects in *hg_repo*
      hg_commits: List of all commit objects in *hg_repo*
      hg_version_tag: Tag object named *hg_version*
      hg_version_commits: List of all commit objects in *hg_repo*
       between *hg_version* tag and the previous one (if any).
    """
    if not hg_repo:
        error('hg: No repository given')

    with hg_open_or_clone_repo(hg_repo) as repo:
        version_tag = None
        version_commits = []
        commits = repo.log()
        tags = [hg_tag(*tag) for tag in repo.tags()]

        if hg_version:
            version_tag, version_commits = \
                hg_version_objects(repo, tags, hg_repo, hg_version)

    return dict(
        hg_repo=repo,
        hg_tags=tags,
        hg_commits=commits,
        hg_repo_path=hg_repo,
        hg_version_tag=version_tag,
        hg_version_commits=version_commits
    )


def chef_start_api():
    """Horribly patches chef api to skip SSL cert validation"""
    from chef.api import ChefRequest

    api = chef.autoconfigure()

    def _request(method, url, data, headers):
        request = ChefRequest(url, data, headers, method=method)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urllib2.urlopen(request, context=ctx).read()

    api._request = _request

    return api


def get_chef_data():
    return fetch_chef_data()


def fetch_chef_data():
    """Return a dict with chef repo data resources

      chef_envs: dict of environments by name. Object has `name`, `attributes`
      and `cookbook_versions`.
      chef_nodes: dict of nodes by name. Object has `name`, `attributes`,
       `chef_environment`, `cookbooks`, `run_list`.
    """
    api = chef_start_api()
    chef_envs = chef.Environment.list()
    chef_nodes = chef.Node.list()

    return dict(
        chef_api=api,
        chef_envs=chef_envs,
        chef_nodes=chef_nodes
    )


def get_apt_data(kwargs):
    required = get_function_args(fetch_apt_data)
    prompt_for_missing_values(kwargs, required)
    return fetch_apt_data(**kwargs)


apt_regex = re.compile(r'''
<a\ href="([^"]+)">[^<]+</a>      # name
\s+
(\d\d-\w\w\w-\d\d\d\d\ \d\d:\d\d) # date
\s+
([\d]+)                           # size
''', re.VERBOSE)


def fetch_apt_package(apt_url, name):
    url = urljoin(apt_url, 'pool', 'main', name[0], name)
    package = dict(name=name, url=url)
    package['versions'] = natsort.natsorted(
        (dict(name=name, date=date, size=size, url=urljoin(url, name))
         for name, date, size in apt_regex.findall(requests.get(url).content)),
        key=lambda v: v['name'])
    return package


def fetch_apt_data(apt_url, apt_packages):
    """Return a dict with apt repo resources

      apt_packages: dict of `dict` with apt packages by name for given
       packages.  dict has `name`, `url` and `versions`. The `versions` entry
       is a list of dict with `name`, `url`, `date`, `size`

    Package names are naturally sorted.
    """
    apt_packages = {name: fetch_apt_package(apt_url, name) for name in apt_packages}
    return dict(apt_packages=apt_packages)


def make_shell(obj, context):
    banner = """\
  __/   .  __  -/- _,_
_(_/(__/__(_,__/__(_/

Template rendering interactive context.

Available vars:
  {}
""".format(', '.join(context.keys()))

    try:
        from IPython import embed
        embed(banner1=banner, user_ns=context)
    except ImportError:
        import code
        import readline  # noqa

        print(banner)
        echo(obj, "Could not load ipython", level='verbose', intend='warning')
        shell = code.InteractiveConsole(context)
        shell.interact()


class Error(click.ClickException):
    def show(self):
        click.secho(self.message, fg='red')


def error(message):
    raise Error(message)


def echo(obj, message, level='normal', intend='info'):
    verbosity = dict(normal=0, verbose=1, debug=2)
    colors = dict(ok='green', warning='orange', error='red')
    if obj['verbose'] >= verbosity.get(level):
        click.secho(message, fg=colors.get(intend.lower()))


def get_function_args(callable):
    return inspect.getargspec(callable).args


def first(collection):
    for item in collection:
        return item


def urljoin(*fragments):
    return '/'.join(s.strip('/') for s in fragments if s)


if __name__ == "__main__":
    cli()
