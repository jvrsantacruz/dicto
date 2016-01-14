from __future__ import print_function

import os
import re
import logging
import traceback
from datetime import datetime

from hamcrest import (assert_that, all_of, has_property, has_properties,
                      anything, contains_inanyorder, contains_string,
                      matches_regexp)

from dicto import cli
from click.testing import CliRunner


logger = logging.getLogger(u'tests.cli')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), u'config.yaml')
EXAMPLES = os.path.join(os.path.dirname(__file__), u'../examples')


class CommandTest(object):
    env = {u'DICTO_CONFIG': CONFIG_FILE}

    def setup(self):
        self.setup_runner()

    def setup_runner(self):
        self.runner = CliRunner(env=self.env)

    def run(self, args, **kwargs):
        logger.info(u'run: dicto ' + u' '.join(args))

        self.result = self.runner.invoke(cli, args, **kwargs)

        if self.result.exit_code:
            logger.info(u'error result: \n' + self.result.output)
        if self.result.exception:
            logger.info(u'exception raised: \n' +
                u''.join(traceback.format_exception(*self.result.exc_info)))

        return self.result

    def assert_result(self, *matchers, **kwargs):
        result = kwargs.get(u'result', self.result)

        assert_that(result, all_of(
            has_property(u'exit_code', kwargs.pop(u'exit_code', 0)),
            has_property(u'output', kwargs.pop(u'output', anything())),
            has_properties(**kwargs),
            *matchers
        ))


class TestCommands(CommandTest):
    def test_command_list(self):
        commands = (u'shell', u'view', u'context')
        has_commands = (has_property(u'name', name) for name in commands)
        assert_that(cli.commands.values(), contains_inanyorder(*has_commands))

    def test_commands_help(self):
        yield self.check_command
        for command in cli.commands.values():
            yield self.check_command, command.name, u'--help'

    def check_command(self, *names):
        self.run(names)
        self.assert_result()


class TestDefaultContext(CommandTest):
    env = {}  # clear config paths in env

    def test_it_outputs_current_date(self):
        self.run(['context'])

        date_to_minutes = str(datetime.now())[:-9]
        self.assert_result(output=contains_string(
            u'current_date: ' + date_to_minutes))


class TestDataOption(CommandTest):
    env = {}  # clear config paths in env

    def test_it_outputs_data_inputs(self):
        """Reflect given extra data"""
        self.run(['context',
                  u'--data', u'key1:value1',
                  u'--data', u'key2:value2'])

        self.assert_result(output=all_of(
            contains_string(u'data:\n'),
            contains_re(r'^\tkey1: value1$'),
            contains_re(r'^\tkey2: value2$'),
        ))

    def test_it_outputs_data_variables(self):
        """Add given data to context"""
        self.run(['context',
                  u'--data', u'key1:value1',
                  u'--data', u'key2:value2'])

        self.assert_result(output=all_of(
            contains_re(r'^key1: value1$'),
            contains_re(r'^key2: value2$'),
        ))


class TestExeOption(CommandTest):
    env = {}  # clear config paths in env

    def test_it_outputs_exe_inputs(self):
        """Reflect given commands"""
        self.run(['context',
                  u'--exe', u'key1:echo value1',
                  u'--exe', u'key2:echo value2'])

        self.assert_result(output=all_of(
            contains_string(u'exe:\n'),
            contains_re(r'^\tkey1: echo value1$'),
            contains_re(r'^\tkey2: echo value2$'),
        ))

    def test_it_outputs_exe_variables(self):
        """Runs given commands and add outputs to context"""
        self.run(['context',
                  u'--exe', u'key1:echo value1',
                  u'--exe', u'key2:echo value2'])

        self.assert_result(output=all_of(
            contains_re(r'^key1: value1'),
            contains_re(r'^key2: value2'),
        ))


class TestFileOption(CommandTest):
    env = {}  # clear config paths in env

    def test_it_outputs_file_variables(self):
        """Runs given commands and add outputs to context"""
        with self.runner.isolated_filesystem() as path:
            file1 = os.path.join(path, u'content1')
            file2 = os.path.join(path, u'content2')

            create_file(file1, u'value1')
            create_file(file2, u'value2')

            self.run(['context',
                      u'--file', u'key1:' + file1,
                      u'--file', u'key2:' + file2])

        self.assert_result(output=all_of(
            contains_re(r'^key1: value1'),
            contains_re(r'^key2: value2'),
        ))


class TestProfileOption(CommandTest):
    env = {}  # clear config paths in env

    def test_it_gets_profile_data(self):
        """Runs given commands and add outputs to context"""
        with self.runner.isolated_filesystem() as path:
            make_config(path, u'.dicto.yaml', contents="""
profiles:
    profile:
        key1: value1
        data:
            key2: value2
        exe:
            key3: echo value3
            """)

            self.run(['context', u'--profile', u'profile'])

        self.assert_result(output=all_of(
            contains_re(r'^key1: value1'),
            contains_re(r'^key2: value2'),
            contains_re(r'^key3: value3'),
        ))


class TestReadConfig(CommandTest):
    env = {}  # clear config paths in env

    def test_it_works_without_config_file(self):
        self.run_with_configs(local=False, project=False, home=False)

        self.assert_config(u'None')

    def test_it_reads_local_config_before_others(self):
        configs = self.run_with_configs(local=True, project=True, home=True)

        self.assert_config(configs['local'])

    def test_it_reads_project_config_before_others(self):
        configs = self.run_with_configs(local=False, project=True, home=True)

        self.assert_config(configs['project'])

    def test_it_reads_home_config_if_no_other(self):
        configs = self.run_with_configs(local=False, project=False, home=True)

        self.assert_config(configs['home'])

    def assert_config(self, path):
        self.assert_result(output=contains_string(
            u'Reading config file from: ' + path))

    def cmd(self, home=None):
        env = {u'DICTO_HOME': home} if home else {}
        self.run([u'--verbose', u'context'], env=env)

    def run_with_configs(self, local, project, home):
        with self.runner.isolated_filesystem() as path:
            paths = make_configs(path, local, project, home)

            self.cmd(home=os.path.join(path, u'home'))

        return paths


def make_configs(path, local, project, home):
    return dict(
        local=make_config(path, u'.dicto.yaml') if local else u'',
        project=make_config(path, u'config.yaml', u'.dicto') if project else u'',
        home=make_config(path, u'config.yaml', u'home') if home else u''
    )


def make_config(path, file, folder=None, contents=''):
    if folder:
        os.mkdir(os.path.join(path, folder))
        file = os.path.join(path, folder, file)
    else:
        file = os.path.join(path, file)

    create_file(file, contents)

    return file


def create_file(path, contents=''):
    with open(path, u'w') as stream:
        stream.write(contents)


def contains_re(text):
    return matches_regexp(re.compile(text, re.MULTILINE))
