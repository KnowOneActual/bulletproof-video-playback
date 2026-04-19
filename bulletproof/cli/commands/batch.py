"""Batch processing command implementation."""

from pathlib import Path

import click

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
@click.option(
    "--resolution",
    help="Override output resolution (e.g., 1920:1080) for exact size matching",
)
@click.option(
    "--audio-sample-rate",
    help="Override audio sample rate (e.g., 48000) for exact hardware matching",
)
def batch(
    input_dir: str,
    profile: str,
    extension: str,
    output_dir: str,
    resolution: str | None,
    audio_sample_rate: str | None,
):
    """Batch process all videos in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path

    if not input_path.is_dir():
        click.echo(f"Error: Input directory not found: {input_dir}", err=True)
        raise SystemExit(1)

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

        # Apply overrides
        if resolution:
            prof.scale = resolution
        if audio_sample_rate:
            prof.audio_sample_rate = audio_sample_rate

        click.echo(f"Profile: {prof.name}\n")

        successful = 0
        failed = 0

        for i, input_file in enumerate(files, 1):
            output_file = output_path / f"{input_file.stem}_output.{prof.extension}"
            click.echo(f"[{i}/{len(files)}] Processing: {input_file.name}")

            try:
                job = TranscodeJob(input_file, output_file, prof)
                if job.sync_execute(show_progress=False):
                    click.echo(f"  Status: SUCCESS (output={output_file.name})")
                    successful += 1
                else:
                    click.echo(f"  Status: FAILED (error={job.error_message})")
                    failed += 1
            except Exception as e:
                click.echo(f"  Status: ERROR (error={e})")
                failed += 1

        click.echo(f"\nBatch processing complete. successful={successful} failed={failed}")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e
