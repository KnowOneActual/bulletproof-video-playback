"""Configuration command implementation."""

import click
from pathlib import Path
from bulletproof.config import ConfigManager
from bulletproof.core import list_profiles


@click.group()
def config():
    """Manage bulletproof configuration.

    Configuration is stored in ~/.bulletproof/config.json
    """
    pass


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
    ConfigManager.set_default_profile(profile)
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
    ConfigManager.set_default_output_dir(output_dir)
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
    ConfigManager.set_speed_preset(preset)
    click.echo(f"✓ Default speed preset set to: {preset}")


@config.command(name="show")
def show_config():
    """Show current configuration.

    EXAMPLES:

    \b
    # View your settings:
    bulletproof config show
    """
    cfg = ConfigManager.show_config()
    click.echo("\nCurrent Configuration:")
    click.echo("=" * 60)
    click.echo(f"Config File: {ConfigManager.CONFIG_FILE}")
    click.echo()
    for key, value in cfg.items():
        if key == "default_output_dir" and value:
            value = Path(value).expanduser()
        click.echo(f"  {key:25} {value}")
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
    if click.confirm(
        "Are you sure? This will reset all your configuration to defaults."
    ):
        ConfigManager.reset()
        click.echo("✓ Configuration reset to defaults")
    else:
        click.echo("Cancelled.")
