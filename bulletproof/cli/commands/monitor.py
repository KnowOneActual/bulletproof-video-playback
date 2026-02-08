"""CLI command for folder monitoring."""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Optional

import click

from bulletproof.config import ConfigError, ConfigLoader


@click.group()
def monitor():
    """Folder monitoring and automatic transcoding."""


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
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default=None,
    help="Override log level",
)
def start(
    config: str,
    watch: Optional[str],
    output: Optional[str],
    poll_interval: Optional[int],
    log_level: Optional[str],
):
    """Start monitoring a folder for new video files.

    The monitor watches a directory for video files and automatically
    transcodes them based on rules defined in the config file.

    Examples:

        # Start with config file
        bulletproof monitor start --config monitor.yaml

        # Override watch directory
        bulletproof monitor start --config monitor.yaml --watch /videos/incoming

        # Override multiple settings
        bulletproof monitor start -c monitor.yaml -w /input -o /output -p 10

        # Run with debug logging
        bulletproof monitor start -c monitor.yaml -l DEBUG
    """
    config_path = Path(config)

    # Build overrides dict
    overrides = {}
    if watch:
        overrides["watch_directory"] = Path(watch)
    if output:
        overrides["output_directory"] = Path(output)
    if poll_interval is not None:
        overrides["poll_interval"] = poll_interval
    if log_level:
        overrides["log_level"] = log_level.upper()

    # Load config and create service
    try:
        service = ConfigLoader.load_and_create(config_path, overrides=overrides)
    except ConfigError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)
    except ImportError as e:
        if "yaml" in str(e).lower():
            click.echo(
                "❌ PyYAML not installed. Install with: pip install pyyaml",
                err=True,
            )
        else:
            click.echo(f"❌ Import error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to load config: {e}", err=True)
        sys.exit(1)

    # Print startup info
    click.echo("🚀 Starting Bulletproof Monitor")
    click.echo(f"   Watch:    {service.config.watch_directory}")
    click.echo(f"   Output:   {service.config.output_directory}")
    click.echo(f"   Interval: {service.config.poll_interval}s")
    click.echo(f"   Rules:    {len(service.config.rules)}")
    click.echo(f"   Log:      {service.config.log_level}")
    if service.config.persist_path:
        click.echo(f"   Queue:    {service.config.persist_path}")
    click.echo("\n⏱️  Monitoring started. Press Ctrl+C to stop.\n")

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        click.echo("\n⏸️  Shutting down gracefully...")
        service.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run service
    try:
        asyncio.run(service.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)

    click.echo("✅ Monitor stopped.")


@monitor.command()
@click.option(
    "--queue",
    "-q",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Queue file (JSON)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed job information",
)
def status(queue: str, verbose: bool):
    """Show status of the transcode queue.

    Examples:

        # Quick status
        bulletproof monitor status --queue queue.json

        # Detailed status with job list
        bulletproof monitor status --queue queue.json --verbose
    """
    queue_path = Path(queue)

    # Load queue
    try:
        with open(queue_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Queue file not found: {queue_path}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON in queue file", err=True)
        sys.exit(1)

    # Parse status from queue structure
    queued_jobs = data.get("queued", [])
    history = data.get("history", [])

    pending = sum(1 for j in queued_jobs if j.get("status") == "pending")
    processing = sum(1 for j in queued_jobs if j.get("status") == "processing")
    completed = sum(1 for j in history if j.get("status") == "complete")
    errored = sum(1 for j in history if j.get("status") == "error")

    # Display summary
    click.echo("📊 Queue Status")
    click.echo("" + "─" * 40)
    click.echo(f"  Pending:      {pending:3d}")
    click.echo(f"  Processing:   {processing:3d}")
    click.echo(f"  Total Queue:  {len(queued_jobs):3d}")
    click.echo("")
    click.echo(f"  Completed:    {completed:3d}")
    click.echo(f"  Errors:       {errored:3d}")
    click.echo(f"  Total History:{len(history):3d}")
    click.echo("" + "─" * 40)

    # Show recent errors if any
    errors = [j for j in history if j.get("status") == "error"]
    if errors:
        click.echo(f"\n⚠️  Recent Errors ({len(errors[-5:])}/{len(errors)}):")
        for job in errors[-5:]:  # Last 5 errors
            input_file = Path(job.get("input_file", "unknown")).name
            error_msg = job.get("error_message", "Unknown error")
            click.echo(f"  • {input_file}")
            click.echo(f"    {error_msg}")

    # Verbose mode: show job details
    if verbose:
        if queued_jobs:
            click.echo("\n📋 Queued Jobs:")
            for i, job in enumerate(queued_jobs[:10], 1):  # First 10
                input_file = Path(job.get("input_file", "unknown")).name
                profile = job.get("profile_name", "unknown")
                status_val = job.get("status", "unknown")
                click.echo(f"  {i}. {input_file} → {profile} ({status_val})")
            if len(queued_jobs) > 10:
                click.echo(f"  ... and {len(queued_jobs) - 10} more")

        if history:
            click.echo("\n📜 Recent History:")
            for i, job in enumerate(history[-10:], 1):  # Last 10
                input_file = Path(job.get("input_file", "unknown")).name
                profile = job.get("profile_name", "unknown")
                status_val = job.get("status", "unknown")
                icon = "✅" if status_val == "complete" else "❌"
                click.echo(f"  {icon} {input_file} → {profile}")

    click.echo("")


@monitor.command()
@click.option(
    "--queue",
    "-q",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Queue file (JSON)",
)
@click.confirmation_option(prompt="Are you sure you want to clear the queue?")
def clear_queue(queue: str):
    """Clear the transcode queue.

    This removes all pending jobs and clears history.
    Processing jobs will complete before the queue is cleared.

    Example:
        bulletproof monitor clear-queue --queue queue.json
    """
    queue_path = Path(queue)

    try:
        # Create empty queue structure
        data = {
            "queued": [],
            "history": [],
            "saved_at": None,
        }
        with open(queue_path, "w") as f:
            json.dump(data, f, indent=2)
        click.echo("✅ Queue cleared")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


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
    help="Default profile for rules",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Config file format",
)
def generate_config(output: str, watch: str, profile: str, format: str):
    """Generate a sample configuration file.

    Creates a starter config with common rules and settings.

    Examples:

        # Generate YAML config
        bulletproof monitor generate-config -o monitor.yaml -w /incoming

        # Generate JSON config
        bulletproof monitor generate-config -o monitor.json -w /videos -f json

        # Use specific profile
        bulletproof monitor generate-config -o config.yaml -w /input -p stream-hd
    """
    output_path = Path(output)

    try:
        ConfigLoader.generate_example(output_path, format=format.lower())
        click.echo(f"✅ Config generated: {output_path}")
        click.echo("\n📝 Edit the file and then run:")
        click.echo(f"   bulletproof monitor start --config {output_path}")
    except ConfigError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
