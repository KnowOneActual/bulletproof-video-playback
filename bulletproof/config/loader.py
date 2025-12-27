"""Configuration loader for folder monitor."""

from pathlib import Path
from typing import Optional, Dict, Any

from bulletproof.core.config import MonitorConfig
from bulletproof.services.monitor_service import MonitorService, MonitorServiceConfig


class ConfigError(Exception):
    """Configuration loading or validation error."""

    pass


class ConfigLoader:
    """Loads configuration from YAML/JSON and creates MonitorService."""

    @staticmethod
    def load_from_file(config_path: Path) -> MonitorConfig:
        """Load config from YAML or JSON file.

        Args:
            config_path: Path to config file (.yaml, .json, or .yml)

        Returns:
            MonitorConfig instance

        Raises:
            ConfigError: If file doesn't exist or is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigError(f"Config file not found: {config_path}")

        suffix = config_path.suffix.lower()

        try:
            if suffix == ".json":
                return MonitorConfig.from_json(config_path)
            elif suffix in (".yaml", ".yml"):
                return MonitorConfig.from_yaml(config_path)
            else:
                raise ConfigError(f"Unsupported config format: {suffix}. Use .yaml, .yml, or .json")
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Failed to load config from {config_path}: {e}")

    @staticmethod
    def validate(config: MonitorConfig) -> None:
        """Validate configuration.

        Args:
            config: MonitorConfig to validate

        Raises:
            ConfigError: If validation fails
        """
        # Check watch directory
        if not config.watch_directory.exists():
            raise ConfigError(f"Watch directory does not exist: {config.watch_directory}")
        if not config.watch_directory.is_dir():
            raise ConfigError(f"Watch directory is not a directory: {config.watch_directory}")

        # Check output directory writable
        try:
            # Try creating a test file
            test_file = config.output_directory / ".bulletproof_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            raise ConfigError(f"Output directory not writable: {config.output_directory}: {e}")

        # Check rules
        if not config.rules:
            raise ConfigError("at least one rule is required")

        for i, rule in enumerate(config.rules):
            if not rule.pattern:
                raise ConfigError(f"Rule {i}: pattern is required")
            if not rule.profile:
                raise ConfigError(f"Rule {i}: profile is required")

        # Check log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if config.log_level.upper() not in valid_levels:
            raise ConfigError(
                f"Invalid log_level: {config.log_level}. Use: {', '.join(valid_levels)}"
            )

    @staticmethod
    def create_service(config: MonitorConfig) -> MonitorService:
        """Create MonitorService from config.

        Args:
            config: MonitorConfig instance

        Returns:
            MonitorService ready to run

        Raises:
            ConfigError: If service creation fails
        """
        try:
            # Convert MonitorConfig rules to rule dicts for MonitorServiceConfig
            # RuleEngine will handle converting these back to Rule objects
            rules_dicts = [
                {
                    "pattern": rule.pattern,
                    "profile": rule.profile,
                    "output_pattern": rule.output_pattern,
                    "pattern_type": rule.pattern_type.value,
                    "delete_input": rule.delete_input,
                    "priority": rule.priority,
                }
                for rule in config.rules
            ]

            # Create service config
            service_config = MonitorServiceConfig(
                watch_directory=config.watch_directory,
                output_directory=config.output_directory,
                rules=rules_dicts,
                poll_interval=config.poll_interval,
                delete_input=config.delete_input,
                persist_path=config.persist_path,
                log_level=config.log_level,
                log_file=config.log_file,
            )

            # Create service
            service = MonitorService(service_config)
            return service

        except Exception as e:
            raise ConfigError(f"Failed to create MonitorService: {e}")

    @staticmethod
    def load_and_create(
        config_path: Path,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> MonitorService:
        """Load config file and create MonitorService in one step.

        Args:
            config_path: Path to config file
            overrides: Optional dict of config overrides (e.g., {"poll_interval": 10})

        Returns:
            MonitorService ready to run

        Raises:
            ConfigError: If loading or validation fails
        """
        # Load config
        config = ConfigLoader.load_from_file(config_path)

        # Apply overrides
        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                else:
                    raise ConfigError(f"Unknown config option: {key}")

        # Validate
        ConfigLoader.validate(config)

        # Create service
        service = ConfigLoader.create_service(config)

        return service

    @staticmethod
    def generate_example(output_path: Path, format: str = "yaml") -> None:
        """Generate example configuration file.

        Args:
            output_path: Where to save example config
            format: Format to use ("yaml" or "json")
        """
        example_data = {
            "watch_directory": "./incoming",
            "output_directory": "./output",
            "poll_interval": 5,
            "delete_input": True,
            "log_level": "INFO",
            "rules": [
                {
                    "pattern": "*_live.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename_no_ext}_qlab.mov",
                    "priority": 100,
                },
                {
                    "pattern": "archive_*.mov",
                    "profile": "archival",
                    "output_pattern": "masters/{filename}",
                    "priority": 90,
                },
                {
                    "pattern": "*.mov",
                    "profile": "standard-playback",
                    "output_pattern": "{filename_no_ext}_converted.mp4",
                    "priority": 1,
                },
            ],
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format.lower() == "yaml":
                # Create temp config to use save_yaml
                # We'll write directly since we have the data
                try:
                    import yaml

                    with open(output_path, "w") as f:
                        yaml.dump(example_data, f, default_flow_style=False, sort_keys=False)
                except ImportError:
                    raise ConfigError("PyYAML not installed. Use format='json' or install PyYAML")
            elif format.lower() == "json":
                import json

                with open(output_path, "w") as f:
                    json.dump(example_data, f, indent=2)
            else:
                raise ConfigError(f"Unsupported format: {format}. Use 'yaml' or 'json'")

            print(f"Example config saved to: {output_path}")
        except Exception as e:
            raise ConfigError(f"Failed to generate example config: {e}")
