"""Textual-based interactive TUI command."""

import click
from bulletproof.tui_textual.app import BulletproofApp


@click.command()
def tui_textual():
    """Rich Textual Terminal UI for professional transcoding.

    Modern interactive interface with:
    - Profile selection with detailed descriptions
    - Real-time file validation
    - Live progress monitoring
    - Settings management
    - Batch processing support

    Keyboard shortcuts:
      Ctrl+Q   - Quit
      Ctrl+N   - New transcode
      Ctrl+B   - Batch process
      D        - Toggle dark mode
      1/2/3    - Navigate screens

    Try: bulletproof tui-textual
    """
    app = BulletproofApp()
    app.run()


if __name__ == "__main__":
    tui_textual()
