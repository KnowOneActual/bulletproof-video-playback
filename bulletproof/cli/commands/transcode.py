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
    help="Output file path (default: input_base_name_output.mov)",
)
@click.option(
    "--list-profiles",
    is_flag=True,
    help="Show available profiles and exit",
)
def transcode(input_file: str, profile: str, output: str, list_profiles_flag: bool):
    """Transcode a video file using a preset profile."""
    if list_profiles_flag:
        profiles = list_profiles()
        click.echo("Available profiles:")
        for name, prof in profiles.items():
            click.echo(f"  {name}: {prof.description}")
        return

    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"Error: Input file not found: {input_file}", err=True)
        raise click.Exit(1)

    if output is None:
        output = str(input_path.parent / f"{input_path.stem}_output.mov")

    output_path = Path(output)

    try:
        prof = get_profile(profile)
        click.echo(f"Profile: {prof.name}")
        click.echo(f"Description: {prof.description}")
        click.echo(f"Input: {input_path}")
        click.echo(f"Output: {output_path}")
        click.echo("Starting transcode...")

        job = TranscodeJob(input_path, output_path, prof)
        success = job.execute()

        if success:
            click.echo(f"✓ Transcode complete: {output_path}")
        else:
            click.echo(f"✗ Transcode failed: {job.error_message}", err=True)
            raise click.Exit(1)

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)
