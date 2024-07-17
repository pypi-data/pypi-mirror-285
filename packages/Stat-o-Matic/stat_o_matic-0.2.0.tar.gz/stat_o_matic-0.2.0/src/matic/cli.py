import rich_click as click
from . import app


def build_cli() -> click.command:
    @click.command()
    def inner_cli() -> None:
        tui = app.StatMatic()
        tui.run()
        return
    fn = inner_cli
    return fn


def main():
    cli = build_cli()
    cli()
