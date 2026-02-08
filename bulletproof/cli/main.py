"""Main CLI entry point."""

import click

from bulletproof import __version__
from bulletproof.cli.commands import analyze, batch, config, monitor, transcode, tui


@click.group()
@click.version_option(version=__version__)
def cli():
    """bulletproof-video-playback: Professional video transcoding for live playback & streaming."""


# Register commands
cli.add_command(transcode)
cli.add_command(analyze)
cli.add_command(batch)
cli.add_command(tui)
cli.add_command(config)
cli.add_command(monitor)


if __name__ == "__main__":
    cli()
