"""Configuration file management for bulletproof."""

import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manage user configuration stored in ~/.bvp/config.json."""

    CONFIG_DIR = Path.home() / ".bvp"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULT_CONFIG = {
        "default_profile": "standard-playback",
        "default_output_dir": None,
        "speed_preset": "normal",  # fast, normal, slow
        "auto_cleanup": True,
    }

    @classmethod
    def ensure_config_dir(cls) -> None:
        """Create config directory if it doesn't exist."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load configuration from file, or return defaults if not found."""
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE) as f:
                    config = json.load(f)
                    # Merge with defaults to handle missing keys
                    return {**cls.DEFAULT_CONFIG, **config}
            except (OSError, json.JSONDecodeError):
                return cls.DEFAULT_CONFIG.copy()
        return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def save(cls, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        cls.ensure_config_dir()
        with open(cls.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a configuration value."""
        config = cls.load()
        config[key] = value
        cls.save(config)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        config = cls.load()
        return config.get(key, default)

    @classmethod
    def get_default_profile(cls) -> str:
        """Get user's default profile."""
        return cls.get("default_profile", "standard-playback")

    @classmethod
    def set_default_profile(cls, profile_name: str) -> None:
        """Set user's default profile."""
        cls.set("default_profile", profile_name)

    @classmethod
    def get_default_output_dir(cls) -> Optional[Path]:
        """Get user's default output directory."""
        dir_str = cls.get("default_output_dir")
        return Path(dir_str) if dir_str else None

    @classmethod
    def set_default_output_dir(cls, output_dir: Path) -> None:
        """Set user's default output directory."""
        cls.set("default_output_dir", str(output_dir))

    @classmethod
    def get_speed_preset(cls) -> str:
        """Get user's speed preset preference."""
        return cls.get("speed_preset", "normal")

    @classmethod
    def set_speed_preset(cls, preset: str) -> None:
        """Set user's speed preset preference."""
        if preset not in ["fast", "normal", "slow"]:
            raise ValueError(f"Invalid preset: {preset}. Must be fast, normal, or slow.")
        cls.set("speed_preset", preset)

    @classmethod
    def show_config(cls) -> dict[str, Any]:
        """Show current configuration."""
        return cls.load()

    @classmethod
    def reset(cls) -> None:
        """Reset configuration to defaults."""
        cls.save(cls.DEFAULT_CONFIG.copy())
