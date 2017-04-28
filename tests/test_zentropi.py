# coding=utf-8

from click.testing import CliRunner

from zentropi.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert 'shell' in result.output
    assert result.exit_code == 0
