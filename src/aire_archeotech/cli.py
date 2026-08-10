import typer

app = typer.Typer(help="AIRE ArcheoTech Hunter evidence-first research CLI.")


@app.callback()
def root() -> None:
    """Research CLI."""


def main() -> None:
    app()
