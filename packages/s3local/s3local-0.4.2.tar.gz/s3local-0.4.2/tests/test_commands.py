import pytest
from s3local import commands
from s3local import constants
from click.testing import CliRunner


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_show_version(runner):
    result = runner.invoke(commands.cli, ["-v"])
    assert result.exit_code == 0
    assert result.output.strip() == constants.VERSION


def test_show_help(runner):
    result = runner.invoke(commands.cli, [])
    assert result.exit_code == 0
    assert "delete" in result.output.strip()
    assert "list" in result.output.strip()
    assert "list-local" in result.output.strip()
    assert "upload" in result.output.strip()
    assert "download" in result.output.strip()
