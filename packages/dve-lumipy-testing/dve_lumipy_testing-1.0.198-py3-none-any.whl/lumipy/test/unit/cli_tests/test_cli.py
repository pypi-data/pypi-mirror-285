import unittest
from click.testing import CliRunner

from lumipy.cli.commands.setup import setup
from lumipy.cli.commands.config import config


class TestCli(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_setup_domain(self):
        result = self.runner.invoke(setup)
        self.assertIn("Setting up python providers", result.stdout)

    def test_setup_domain_with_domain(self):
        result = self.runner.invoke(setup, ['--domain', 'fbn-ci'])
        self.assertIn("Setting up python providers", result.stdout)

    def test_add_good_config(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci-fake_', '--token', 'NTBhYzIwODEwN2JkNGVhMWI1ZDBhZTVmYTcxMTEyZWV8==', '--overwrite'])
        self.assertIsNone(result.exception)

    def test_add_good_domain_bad_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_good_domain_empty_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', ''])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_good_domain_none_token(self):
        result = self.runner.invoke(config, ['add', '--domain', 'fbn-ci', '--token', None])
        self.assertEqual(result.exception.args[0], 'Invalid PAT')

    def test_add_bad_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', 'https://fbn-ci.lusid.com/app', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: https://fbn-ci.lusid.com/app')

    def test_add_empty_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', '', '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: ')

    def test_add_none_domain(self):
        result = self.runner.invoke(config, ['add', '--domain', None, '--token', '3/   //ZX'])
        self.assertEqual(result.exception.args[0], 'Invalid domain provided: None')
