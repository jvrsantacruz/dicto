from __future__ import print_function
from __future__ import unicode_literals

import os
import logging
import traceback

from hamcrest import assert_that, all_of, has_property, has_properties, anything

from dicto import cli
from click.testing import CliRunner


logger = logging.getLogger('tests.cli')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.yaml')


class CommandTest(object):
    def setup(self):
        self.setup_runner()

    def setup_runner(self):
        self.runner = CliRunner(env={'DICTO_CONFIG': CONFIG_FILE})

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
        result = kwargs.get('result', self.result)

        assert_that(result, all_of(
            has_property('exit_code', kwargs.pop('exit_code', 0)),
            has_property('output', kwargs.pop('output', anything())),
            has_properties(**kwargs),
            *matchers
        ))


class TestCommands(CommandTest):
    def test_commands_help(self):
        yield self.check_command
        for command in cli.commands.values():
            yield self.check_command, command.name, '--help'

    def check_command(self, *names):
        self.run(names)
        self.assert_result()
