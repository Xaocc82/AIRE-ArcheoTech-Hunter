from typer.testing import CliRunner

from aire_archeotech.cli import app


def test_cli_prints_project_identity() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "AIRE ArcheoTech Hunter" in result.output
