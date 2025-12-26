"""CLI command for folder monitoring."""

import asyncio
import json
import signal
from pathlib import Path
from typing import Optional

import click

from bulletproof.core.config import MonitorConfig
from bulletproof.services.monitor_service import MonitorService


@click.group()
def monitor():
    """Folder monitoring and automatic transcoding."""
    pass


@monitor.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Config file (YAML or JSON)",
)
@click.option(
    "--watch",
    "-w",
    type=click.Path(exists=True, file_okay=False),
    help="Override watch directory",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False),
    help="Override output directory",
)
@click.option(
    "--poll-interval",
    "-p",
    type=int,
    default=None,
    help="Override poll interval (seconds)",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default=None,
    help="Override log level",
)
def start(config: str, watch: Optional[str], output: Optional[str], poll_interval: Optional[int], log_level: Optional[str]):
    """Start monitoring a folder for new video files.
    
    Example:
        bulletproof monitor start --config theater.yaml
        bulletproof monitor start --config theater.yaml --watch /input --output /output
    """
    config_path = Path(config)

    # Load config
    if config_path.suffix.lower() == ".yaml" or config_path.suffix.lower() == ".yml":
        try:
            monitor_config = MonitorConfig.from_yaml(config_path)
        except ImportError:
            click.echo(
                "Error: PyYAML not installed. Install with: pip install pyyaml",
                err=True,
            )
            raise click.Exit(1)
    elif config_path.suffix.lower() == ".json":
        monitor_config = MonitorConfig.from_json(config_path)
    else:
        click.echo(
            f"Error: Unknown config format. Use .yaml or .json",
            err=True,
        )
        raise click.Exit(1)

    # Override with CLI args
    if watch:
        monitor_config.watch_directory = Path(watch)
    if output:
        monitor_config.output_directory = Path(output)
    if poll_interval is not None:
        monitor_config.poll_interval = poll_interval
    if log_level:
        monitor_config.log_level = log_level

    # Validate after overrides
    try:
        monitor_config.__post_init__()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)

    # Create service
    service = MonitorService(monitor_config)

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        click.echo("\n⏸️  Shutting down...")
        service.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run service
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)


@monitor.command()
@click.option(
    "--queue",
    "-q",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Queue file (JSON)",
)
def status(queue: str):
    """Show status of the transcode queue.
    
    Example:
        bulletproof monitor status --queue queue.json
    """
    queue_path = Path(queue)

    # Load queue
    try:
        with open(queue_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        click.echo(f"Error: Queue file not found: {queue_path}", err=True)
        raise click.Exit(1)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON in queue file", err=True)
        raise click.Exit(1)

    # Parse status
    pending = len([j for j in data.get("jobs", []) if j.get("status") == "PENDING"])
    processing = len([j for j in data.get("jobs", []) if j.get("status") == "PROCESSING"])
    completed = len([j for j in data.get("jobs", []) if j.get("status") == "COMPLETE"])
    error = len([j for j in data.get("jobs", []) if j.get("status") == "ERROR"])

    click.echo("⚏ Queue Status")
    click.echo(f"  Pending:    {pending:3d}")
    click.echo(f"  Processing: {processing:3d}")
    click.echo(f"  Completed:  {completed:3d}")
    click.echo(f"  Errors:     {error:3d}")

    # Show recent errors if any
    errors = [j for j in data.get("jobs", []) if j.get("status") == "ERROR"]
    if errors:
        click.echo("\n⚠️  Recent Errors:")
        for job in errors[-3:]:  # Last 3 errors
            click.echo(f"  - {job.get('input_file')}: {job.get('error', 'Unknown error')}")


@monitor.command()
@click.option(
    "--queue",
    "-q",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Queue file (JSON)",
)
@click.confirmation_option(
    prompt="Are you sure you want to clear the queue?"
)
def clear_queue(queue: str):
    """Clear the transcode queue.
    
    Example:
        bulletproof monitor clear-queue --queue queue.json
    """
    queue_path = Path(queue)

    try:
        data = {"jobs": [], "version": 1, "last_updated": None}
        with open(queue_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        click.echo(✅ Queue cleared")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)


@monitor.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output config file path",
)
@click.option(
    "--watch",
    "-w",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="Watch directory",
)
@click.option(
    "--profile",
    "-p",
    default="live-qlab",
    help="Default profile",
)
def generate_config(output: str, watch: str, profile: str):
    """Generate a sample configuration file.
    
    Example:
        bulletproof monitor generate-config --output monitor.yaml --watch /input
    """
    output_path = Path(output)
    output_dir = output_path.parent

    # Determine format
    if output_path.suffix.lower() in [".yaml", ".yml"]:
        sample_config = f"""# Bulletproof Monitor Configuration

watch_directory: {watch}
output_directory: ./output
poll_interval: 5
delete_input: true
log_level: INFO

rules:
  - pattern: "*_live.mov"
    profile: {profile}
    output_pattern: "{{filename_no_ext}}_qlab.mov"
    priority: 100
  
  - pattern: "archive_*.mov"
    profile: archive-prores
    output_pattern: "masters/{{filename}}"
    priority: 90
"""
    else:
        sample_config = f"""{
  "watch_directory": "{watch}",
  "output_directory": "./output",
  "poll_interval": 5,
  "delete_input": true,
  "log_level": "INFO",
  "rules": [
    {{
      "pattern": "*_live.mov",
      "profile": "{profile}",
      "output_pattern": "{{filename_no_ext}}_qlab.mov",
      "priority": 100
    }},
    {{
      "pattern": "archive_*.mov",
      "profile": "archive-prores",
      "output_pattern": "masters/{{filename}}",
      "priority": 90
    }}
  ]
}}
"""

    # Write file
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(sample_config)
        click.echo(f✅ Config generated: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Exit(1)
