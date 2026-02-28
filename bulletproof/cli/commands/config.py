"""Configuration command implementation.

NOTE: This command is deprecated in favor of YAML config files.
Use 'bulletproof monitor generate-config' for folder monitoring.
This is kept for backward compatibility with simple transcode workflow.
"""

import json
from pathlib import Path

import click

from bulletproof.core import list_profiles

# Simple config file manager (replaces old ConfigManager)
CONFIG_FILE = Path.home() / ".bulletproof" / "config.json"


def _load_config():
    """Load config from file."""
    if not CONFIG_FILE.exists():
        return {
            "default_profile": "live-qlab",
            "default_output_dir": None,
            "speed_preset": "normal",
        }
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {
            "default_profile": "live-qlab",
            "default_output_dir": None,
            "speed_preset": "normal",
        }


def _save_config(config):
    """Save config to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


@click.group()
def config():
    """Manage bulletproof configuration.

    Configuration is stored in ~/.bulletproof/config.json

    NOTE: For folder monitoring, use YAML config files:
      bulletproof monitor generate-config -o monitor.yaml -w ./incoming
    """


@config.command()
@click.argument("profile", type=click.Choice(list(list_profiles().keys())))
def set_default_profile(profile: str):
    """Set your default transcoding profile.

    EXAMPLES:

    \b
    # Set QLab as your default:
    bulletproof config set-default-profile live-qlab

    \b
    # Set streaming as your default:
    bulletproof config set-default-profile stream-hd
    """
    cfg = _load_config()
    cfg["default_profile"] = profile
    _save_config(cfg)
    click.echo(f"✓ Default profile set to: {profile}")


@config.command()
@click.argument("output_dir", type=click.Path(path_type=Path))
def set_output_dir(output_dir: Path):
    """Set your default output directory.

    EXAMPLES:

    \b
    # Set output folder:
    bulletproof config set-output-dir ~/Videos/processed

    \b
    # Set to external drive:
    bulletproof config set-output-dir /Volumes/archive/videos
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = _load_config()
    cfg["default_output_dir"] = str(output_dir)
    _save_config(cfg)
    click.echo(f"✓ Default output directory set to: {output_dir}")


@config.command()
@click.argument("preset", type=click.Choice(["fast", "normal", "slow"]))
def set_preset(preset: str):
    """Set your default speed preset.

    EXAMPLES:

    \b
    # For time-sensitive live playback:
    bulletproof config set-preset fast

    \b
    # For maximum quality:
    bulletproof config set-preset slow
    """
    cfg = _load_config()
    cfg["speed_preset"] = preset
    _save_config(cfg)
    click.echo(f"✓ Default speed preset set to: {preset}")


@config.command(name="show")
def show_config():
    """Show current configuration.

    EXAMPLES:

    \b
    # View your settings:
    bulletproof config show
    """
    cfg = _load_config()
    click.echo("\nCurrent Configuration:")
    click.echo("=" * 60)
    click.echo(f"Config File: {CONFIG_FILE}")
    click.echo()
    for key, value in cfg.items():
        if key == "default_output_dir" and value:
            value = Path(value).expanduser()
        click.echo(f"  {key:25} {value}")
    click.echo()
    click.echo("\nFor folder monitoring, use YAML config files:")
    click.echo("  bulletproof monitor generate-config -o monitor.yaml -w ./incoming")
    click.echo()


@config.command()
def reset():
    """Reset configuration to defaults.

    WARNING: This will erase all your saved preferences!

    EXAMPLES:

    \b
    # Reset to factory defaults:
    bulletproof config reset
    """
    if click.confirm("Are you sure? This will reset all your configuration to defaults."):
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        click.echo("✓ Configuration reset to defaults")
    else:
        click.echo("Cancelled.")
