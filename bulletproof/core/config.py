"""Configuration system for folder monitoring."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from bulletproof.core.rules import PatternType, Rule


@dataclass
class MonitorConfig:
    """Configuration for folder monitoring."""

    watch_directory: Path
    output_directory: Path
    rules: List[Rule] = field(default_factory=list)
    poll_interval: int = 5  # seconds
    persist_path: Optional[Path] = None  # queue.json location
    delete_input: bool = True  # Delete input after successful transcode
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    def __post_init__(self):
        """Validate and normalize paths."""
        self.watch_directory = Path(self.watch_directory)
        self.output_directory = Path(self.output_directory)

        if self.log_file:
            self.log_file = Path(self.log_file)

        if self.persist_path:
            self.persist_path = Path(self.persist_path)

        # Validate
        if not self.watch_directory.exists():
            raise FileNotFoundError(f"Watch directory does not exist: {self.watch_directory}")
        if not self.watch_directory.is_dir():
            raise NotADirectoryError(f"Watch directory is not a directory: {self.watch_directory}")

        # Create output directory if it doesn't exist
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "watch_directory": str(self.watch_directory),
            "output_directory": str(self.output_directory),
            "poll_interval": self.poll_interval,
            "persist_path": str(self.persist_path) if self.persist_path else None,
            "delete_input": self.delete_input,
            "log_level": self.log_level,
            "log_file": str(self.log_file) if self.log_file else None,
            "rules": [
                {
                    "pattern": r.pattern,
                    "profile": r.profile,
                    "output_pattern": r.output_pattern,
                    "pattern_type": r.pattern_type.value,
                    "delete_input": r.delete_input,
                    "priority": r.priority,
                }
                for r in self.rules
            ],
        }

    @classmethod
    def from_yaml(cls, path: Path) -> "MonitorConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML config file

        Returns:
            MonitorConfig instance

        Raises:
            ImportError: If PyYAML not installed
            FileNotFoundError: If config file not found
        """
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required for YAML config. Install with: pip install pyyaml"
            )

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return cls._from_dict(data, config_dir=path.parent)

    @classmethod
    def from_json(cls, path: Path) -> "MonitorConfig":
        """Load configuration from JSON file.

        Args:
            path: Path to JSON config file

        Returns:
            MonitorConfig instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        return cls._from_dict(data, config_dir=path.parent)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any], config_dir: Path = Path(".")) -> "MonitorConfig":
        """Create from dictionary (handles both YAML and JSON).

        Args:
            data: Configuration dictionary
            config_dir: Directory for relative path resolution

        Returns:
            MonitorConfig instance
        """

        # Resolve relative paths from config directory
        def resolve_path(p: Optional[str]) -> Optional[Path]:
            if not p:
                return None
            p_obj = Path(p)
            if p_obj.is_absolute():
                return p_obj
            return (config_dir / p_obj).resolve()

        watch_dir = resolve_path(data.get("watch_directory"))
        output_dir = resolve_path(data.get("output_directory"))

        if not watch_dir:
            raise ValueError("watch_directory is required")
        if not output_dir:
            raise ValueError("output_directory is required")

        # Parse rules
        rules = []
        for rule_data in data.get("rules", []):
            rule = Rule(
                pattern=rule_data.get("pattern", ""),
                profile=rule_data.get("profile", ""),
                output_pattern=rule_data.get("output_pattern", "{filename}"),
                pattern_type=PatternType(rule_data.get("pattern_type", "glob")),
                delete_input=rule_data.get("delete_input", True),
                priority=rule_data.get("priority", 100),
            )
            rules.append(rule)

        # Create config
        return cls(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=rules,
            poll_interval=data.get("poll_interval", 5),
            persist_path=resolve_path(data.get("persist_path")),
            delete_input=data.get("delete_input", True),
            log_level=data.get("log_level", "INFO"),
            log_file=resolve_path(data.get("log_file")),
        )

    def save_yaml(self, path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            path: Path where to save YAML file
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def save_json(self, path: Path) -> None:
        """Save configuration to JSON file.

        Args:
            path: Path where to save JSON file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
