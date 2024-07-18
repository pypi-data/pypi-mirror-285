import pytest
from click.testing import CliRunner

from mksite import cli


@pytest.fixture(scope="module")
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def patch_write_to_filesystem(monkeypatch: pytest.MonkeyPatch):
    def patch(*args, **kwargs):
        pass

    monkeypatch.setattr(cli.persistence, "write_to_filesystem", patch)


def test_build_command(cli_runner: CliRunner):
    result = cli_runner.invoke(cli.build, ["--dir", "tests/example"])

    expected_output = """\
Start building site…
Files written to 'public' directory.
"""

    assert result.exit_code == 0
    assert result.output == expected_output
