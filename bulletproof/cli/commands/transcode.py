"""Transcode command implementation."""

from pathlib import Path

import click

from bulletproof.core import TranscodeJob, get_profile, list_profiles

# Note: ConfigManager is legacy - removed in favor of YAML config files
# This command uses in-memory defaults for simplicity


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--profile",
    default="live-qlab",  # Default profile
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
    "--preset",
    "-p",
    type=click.Choice(["fast", "normal", "slow"]),
    default="normal",
    help="Speed preset: fast (quick, slight quality loss), normal (default), slow (best quality)",
)
@click.option(
    "--resolution",
    help="Override output resolution (e.g., 1920:1080) for exact size matching",
)
@click.option(
    "--audio-sample-rate",
    help="Override audio sample rate (e.g., 48000) for exact hardware matching",
)
@click.option(
    "--list-profiles",
    is_flag=True,
    help="Show available profiles and exit",
)
def transcode(
    input_file: str,
    profile: str,
    output: str,
    preset: str,
    resolution: str | None,
    audio_sample_rate: str | None,
    list_profiles_flag: bool,
):
    """Transcode a video file using a preset profile.

    EXAMPLES:

    \b
    # Prepare video for QLab (ProRes Proxy, QLab recommended):
    bvp transcode video.mov --profile live-qlab

    \b
    # Prepare video for streaming (H.265, 1080p, small file size):
    bvp transcode video.mov --profile stream-hd --output stream_version.mp4

    \b
    # Fast encode for time-sensitive live playback:
    bvp transcode video.mov --profile live-qlab --preset fast

    \b
    # Prepare video for general playback (H.264, works everywhere):
    bvp transcode video.mov --profile standard-playback

    \b
    # Archive with maximum quality (ProRes HQ, lossless, slow):
    bvp transcode video.mov --profile archival --preset slow

    \b
    # List all available profiles:
    bvp transcode --list-profiles
    """
    if list_profiles_flag:
        profiles = list_profiles()
        click.echo("\nAvailable profiles:")
        click.echo("=" * 60)
        for name, prof in profiles.items():
            click.echo(f"  {name:20} {prof.description}")
            click.echo(f"  {'':20} Codec: {prof.codec}, Extension: .{prof.extension}")
            click.echo()
        return

    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"Error: Input file not found: {input_file}", err=True)
        raise SystemExit(1)

    if output is None:
        prof = get_profile(profile)
        output = str(
            input_path.parent / f"{input_path.stem}__processed__{profile}.{prof.extension}"
        )

    output_path = Path(output)

    try:
        prof = get_profile(profile)

        # Apply overrides
        if resolution:
            prof.scale = resolution
        if audio_sample_rate:
            prof.audio_sample_rate = audio_sample_rate

        click.echo(f"\nProfile: {prof.name}")
        click.echo(f"Description: {prof.description}")
        click.echo(f"Speed Preset: {preset}")
        click.echo(f"Input: {input_path}")
        click.echo(f"Output: {output_path}")
        click.echo("\nStarting transcode...")

        job = TranscodeJob(input_path, output_path, prof, speed_preset=preset)
        success = job.sync_execute()

        if success:
            click.echo(f"Transcode successful: {output_path}")
        else:
            click.echo(f"Transcode failed: {job.error_message}", err=True)
            raise SystemExit(1)

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e
