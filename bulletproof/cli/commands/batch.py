"""Batch processing command implementation."""

import click
from pathlib import Path
from bulletproof.core import TranscodeJob, get_profile, list_profiles


@click.command()
@click.argument("input_dir", type=click.Path(exists=True))
@click.option(
    "--profile",
    default="standard-playback",
    help="Profile to use for transcode",
    type=click.Choice(list(list_profiles().keys())),
)
@click.option(
    "--extension",
    "-e",
    default=".mov",
    help="File extension to match (e.g., .mov, .mp4)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory (default: input_dir)",
)
def batch(input_dir: str, profile: str, extension: str, output_dir: str):
    """Batch process all videos in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path

    if not input_path.is_dir():
        click.echo(f"Error: Input directory not found: {input_dir}", err=True)
        raise click.Exit(1)

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    # Find all matching files
    files = list(input_path.glob(f"*{extension}"))
    if not files:
        click.echo(f"No files matching *{extension} found in {input_dir}")
        return

    click.echo(f"Found {len(files)} file(s) to process")

    try:
        prof = get_profile(profile)
        click.echo(f"Profile: {prof.name}\n")

        successful = 0
        failed = 0

        for i, input_file in enumerate(files, 1):
            output_file = output_path / f"{input_file.stem}_output.mov"
            click.echo(f"[{i}/{len(files)}] Processing: {input_file.name}")

            try:
                job = TranscodeJob(input_file, output_file, prof)
                if job.execute():
                    click.echo(f"  ✓ Complete: {output_file.name}")
                    successful += 1
                else:
                    click.echo(f"  ✗ Failed: {job.error_message}")
                    failed += 1
            except Exception as e:
                click.echo(f"  ✗ Error: {e}")
                failed += 1

        click.echo(f"\nBatch complete: {successful} successful, {failed} failed")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)
