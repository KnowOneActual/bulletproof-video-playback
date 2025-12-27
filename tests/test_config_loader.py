"""Tests for ConfigLoader."""

import json
import pytest
from pathlib import Path

from bulletproof.config import ConfigLoader, ConfigError
from bulletproof.core.rules import PatternType


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_load_yaml_config(self, tmp_path):
        """Test loading YAML config file."""
        pytest.importorskip("yaml", reason="PyYAML not installed")
        import yaml

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "test.yaml"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "poll_interval": 10,
            "delete_input": False,
            "log_level": "DEBUG",
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename_no_ext}_qlab.mov",
                    "priority": 100,
                }
            ],
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = ConfigLoader.load_from_file(config_file)
        assert config.poll_interval == 10
        assert config.delete_input is False
        assert config.log_level == "DEBUG"
        assert len(config.rules) == 1
        assert config.rules[0].profile == "live-qlab"

    def test_load_json_config(self, tmp_path):
        """Test loading JSON config file."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "test.json"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "poll_interval": 5,
            "rules": [
                {
                    "pattern": "archive_*.mov",
                    "profile": "archival",
                    "output_pattern": "masters/{filename}",
                    "priority": 90,
                }
            ],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_from_file(config_file)
        assert config.poll_interval == 5
        assert len(config.rules) == 1
        assert config.rules[0].pattern == "archive_*.mov"

    def test_load_nonexistent_file(self, tmp_path):
        """Test error when config file doesn't exist."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(ConfigError, match="not found"):
            ConfigLoader.load_from_file(config_file)

    def test_load_unsupported_format(self, tmp_path):
        """Test error for unsupported file format."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "test.txt"
        config_file.write_text("invalid")

        with pytest.raises(ConfigError, match="Unsupported config format"):
            ConfigLoader.load_from_file(config_file)

    def test_validate_missing_watch_directory(self, tmp_path):
        """Test validation fails for nonexistent watch directory."""
        from bulletproof.core.config import MonitorConfig
        from bulletproof.core.rules import Rule

        watch_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"

        rule = Rule(pattern="*.mov", profile="test", output_pattern="{filename}")

        # Should raise during __post_init__
        with pytest.raises(FileNotFoundError):
            MonitorConfig(
                watch_directory=watch_dir,
                output_directory=output_dir,
                rules=[rule],
            )

    def test_validate_no_rules(self, tmp_path):
        """Test validation fails when no rules defined."""
        from bulletproof.core.config import MonitorConfig

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[],  # No rules
        )

        with pytest.raises(ConfigError, match="at least one rule"):
            ConfigLoader.validate(config)

    def test_validate_invalid_log_level(self, tmp_path):
        """Test validation fails for invalid log level."""
        from bulletproof.core.config import MonitorConfig
        from bulletproof.core.rules import Rule

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        rule = Rule(pattern="*.mov", profile="test", output_pattern="{filename}")

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[rule],
            log_level="INVALID",
        )

        with pytest.raises(ConfigError, match="Invalid log_level"):
            ConfigLoader.validate(config)

    def test_create_service(self, tmp_path):
        """Test creating MonitorService from config."""
        from bulletproof.core.config import MonitorConfig
        from bulletproof.core.rules import Rule

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        rule = Rule(pattern="*.mov", profile="live-qlab", output_pattern="{filename}")

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[rule],
        )

        service = ConfigLoader.create_service(config)
        assert service is not None
        assert service.monitor is not None
        assert service.queue is not None

    def test_load_and_create(self, tmp_path):
        """Test loading config and creating service in one step."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "test.json"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        service = ConfigLoader.load_and_create(config_file)
        assert service is not None

    def test_load_and_create_with_overrides(self, tmp_path):
        """Test loading config with runtime overrides."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        override_watch = tmp_path / "override_watch"
        override_watch.mkdir()

        config_file = tmp_path / "test.json"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "poll_interval": 5,
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        overrides = {
            "watch_directory": override_watch,
            "poll_interval": 10,
        }

        service = ConfigLoader.load_and_create(config_file, overrides=overrides)
        assert service.config.watch_directory == override_watch
        assert service.config.poll_interval == 10

    def test_generate_example_yaml(self, tmp_path):
        """Test generating example YAML config."""
        pytest.importorskip("yaml", reason="PyYAML not installed")

        output_file = tmp_path / "example.yaml"
        ConfigLoader.generate_example(output_file, format="yaml")

        assert output_file.exists()
        assert output_file.read_text().startswith("watch_directory:")

    def test_generate_example_json(self, tmp_path):
        """Test generating example JSON config."""
        output_file = tmp_path / "example.json"
        ConfigLoader.generate_example(output_file, format="json")

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "watch_directory" in data
        assert "rules" in data

    def test_relative_paths_resolved(self, tmp_path):
        """Test that relative paths are resolved from config directory."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "test.json"
        config_data = {
            "watch_directory": "./watch",  # Relative path
            "output_directory": "./output",  # Relative path
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = ConfigLoader.load_from_file(config_file)
        # Paths should be absolute
        assert config.watch_directory.is_absolute()
        assert config.output_directory.is_absolute()
