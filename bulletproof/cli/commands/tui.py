"""Interactive TUI command."""

import click

from bulletproof.tui.main import TUIApp


@click.command()
def tui():
    """Interactive terminal UI for transcode wizard.

    Guides you through selecting input file, profile, and output path.
    """
    app = TUIApp()
    app.run()


if __name__ == "__main__":
    tui()
