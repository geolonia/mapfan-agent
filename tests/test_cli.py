from typer.testing import CliRunner
from mapfan_agent.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.stdout


def test_cli_no_args_shows_help():
    result = runner.invoke(app, [])
    assert result.exit_code in (0, 2)
    assert "mapfan-agent" in result.stdout.lower() or "Usage" in result.stdout
