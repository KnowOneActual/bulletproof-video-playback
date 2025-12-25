"""Transcode command implementation."""

import click
from pathlib import Path
from bulletproof.core import TranscodeJob, get_profile, list_profiles


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--profile",
    default="standard-playback",
    help="Profile to use for transcode",
    type=click.Choice(list(list_profiles().keys())),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: input_base_name__processed__profile.ext)",
)
@click.option(
    "--list-profiles",
    is_flag=True,
    help="Show available profiles and exit",
)
def transcode(input_file: str, profile: str, output: str, list_profiles_flag: bool):
    """Transcode a video file using a preset profile.

    EXAMPLES:

    \b
    # Prepare video for QLab (ProRes Proxy, QLab recommended):
    bulletproof transcode video.mov --profile live-qlab

    \b
    # Prepare video for streaming (H.265, 1080p, small file size):
    bulletproof transcode video.mov --profile stream-hd --output stream_version.mp4

    \b
    # Prepare video for general playback (H.264, works everywhere):
    bulletproof transcode video.mov --profile standard-playback

    \b
    # Archive with maximum quality (ProRes HQ, lossless):
    bulletproof transcode video.mov --profile archival --output archived.mov

    \b
    # List all available profiles:
    bulletproof transcode --list-profiles
    """
    if list_profiles_flag:
        profiles = list_profiles()
        click.echo("\nAvailable profiles:")
        click.echo("="*60)
        for name, prof in profiles.items():
            click.echo(f"  {name:20} {prof.description}")
            click.echo(f"  {'':20} Codec: {prof.codec}, Extension: .{prof.extension}")
            click.echo()
        return

    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"Error: Input file not found: {input_file}", err=True)
        raise click.Exit(1)

    if output is None:
        prof = get_profile(profile)
        output = str(
            input_path.parent
            / f"{input_path.stem}__processed__{profile}.{prof.extension}"
        )

    output_path = Path(output)

    try:
        prof = get_profile(profile)
        click.echo(f"\nProfile: {prof.name}")
        click.echo(f"Description: {prof.description}")
        click.echo(f"Input: {input_path}")
        click.echo(f"Output: {output_path}")
        click.echo("\nStarting transcode...")

        job = TranscodeJob(input_path, output_path, prof)
        success = job.execute()

        if success:
            click.echo(f"\n✓ Transcode complete: {output_path}")
        else:
            click.echo(f"\n✗ Transcode failed: {job.error_message}", err=True)
            raise click.Exit(1)

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)
