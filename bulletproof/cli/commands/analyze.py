"""Analyze command implementation."""

import click
import subprocess
import json
from pathlib import Path


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
def analyze(input_file: str):
    """Analyze a video file and show codec information."""
    input_path = Path(input_file)

    if not input_path.exists():
        click.echo(f"Error: Input file not found: {input_file}", err=True)
        raise click.Exit(1)

    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(input_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        click.echo(f"File: {input_path}")
        click.echo(f"Format: {data.get('format', {}).get('format_name', 'Unknown')}")
        click.echo(f"Duration: {data.get('format', {}).get('duration', 'Unknown')}s")
        click.echo(f"Bitrate: {data.get('format', {}).get('bit_rate', 'Unknown')} bps")
        click.echo("\nStreams:")

        for i, stream in enumerate(data.get("streams", [])):
            codec_type = stream.get("codec_type")
            codec_name = stream.get("codec_name")
            click.echo(f"  Stream {i}: {codec_type} ({codec_name})")
            if codec_type == "video":
                click.echo(f"    Resolution: {stream.get('width')}x{stream.get('height')}")
                click.echo(f"    FPS: {stream.get('r_frame_rate', 'Unknown')}")
                click.echo(f"    Pixel Format: {stream.get('pix_fmt', 'Unknown')}")
            elif codec_type == "audio":
                click.echo(f"    Sample Rate: {stream.get('sample_rate', 'Unknown')} Hz")
                click.echo(f"    Channels: {stream.get('channels', 'Unknown')}")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error analyzing file: {e.stderr}", err=True)
        raise click.Exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)
