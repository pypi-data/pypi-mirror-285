import pytest
from click.testing import CliRunner

from taskblaster.cli import cli as cli_toplevel


class CLI:
    def __init__(self):
        self.clirunner = CliRunner()

    def __call__(self, args):
        command = cli_toplevel.commands[args[0]]
        return self.clirunner.invoke(command, args[1:])


@pytest.fixture()
def cli_uninitialized(testdir):
    return CLI()


def test_init(cli_uninitialized):
    result = cli_uninitialized(['init'])
    assert result.exit_code == 0
    assert result.output.startswith('Created repository')


@pytest.fixture()
def cli(cli_uninitialized):
    cli_uninitialized(['init'])
    return cli_uninitialized


def test_error_uninitialized(cli_uninitialized):
    x = cli_uninitialized(['ls'])
    assert x.exit_code != 0
    assert x.output.startswith('Error: No registry')


def test_info(cli):
    result = cli(['info'])
    print(result.output)
    assert result.exit_code == 0
    assert result.output.startswith('Module:')
