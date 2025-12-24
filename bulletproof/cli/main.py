"""Main CLI entry point."""

import click
from bulletproof import __version__
from bulletproof.cli.commands import transcode, analyze, batch


@click.group()
@click.version_option(version=__version__)
def cli():
    """bulletproof-video-playback: Professional video transcoding for theater & streaming."""
    pass


# Register commands
cli.add_command(transcode)
cli.add_command(analyze)
cli.add_command(batch)


if __name__ == "__main__":
    cli()
