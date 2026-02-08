"""Rule engine for mapping files to transcode profiles."""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class PatternType(str, Enum):
    """Pattern matching type."""

    GLOB = "glob"  # *.mov style
    REGEX = "regex"  # regex pattern
    EXACT = "exact"  # exact filename match


@dataclass
class Rule:
    """A rule mapping file patterns to profiles."""

    pattern: str
    profile: str
    output_pattern: str = "{filename}"  # {filename}, {filename_no_ext}, {stem}
    pattern_type: PatternType = PatternType.GLOB
    delete_input: bool = True  # Delete input after successful transcode
    priority: int = 100  # Higher priority = checked first

    def matches(self, filename: str) -> bool:
        """Check if filename matches this rule.

        Args:
            filename: Filename to check (basename only)

        Returns:
            True if pattern matches
        """
        if self.pattern_type == PatternType.EXACT:
            return filename == self.pattern
        elif self.pattern_type == PatternType.REGEX:
            try:
                return bool(re.match(self.pattern, filename))
            except re.error:
                return False
        else:  # GLOB
            # Convert glob pattern to regex
            regex_pattern = self._glob_to_regex(self.pattern)
            try:
                return bool(re.match(regex_pattern, filename))
            except re.error:
                return False

    def get_output_path(self, input_path: Path, output_dir: Path) -> Path:
        """Get output path based on input and pattern.

        Args:
            input_path: Input file path
            output_dir: Output directory

        Returns:
            Output file path
        """
        filename = input_path.name
        filename_no_ext = input_path.stem

        # Replace placeholders
        output_name = self.output_pattern.format(
            filename=filename,
            filename_no_ext=filename_no_ext,
            stem=filename_no_ext,  # alias for filename_no_ext
        )

        # Handle nested directories in output pattern
        if "/" in output_name or "\\" in output_name:
            return output_dir / output_name
        else:
            return output_dir / output_name

    @staticmethod
    def _glob_to_regex(glob_pattern: str) -> str:
        """Convert glob pattern to regex.

        Args:
            glob_pattern: Glob pattern like *.mov

        Returns:
            Regex pattern string
        """
        # Escape special regex characters except * and ?
        pattern = glob_pattern
        pattern = re.escape(pattern)
        # Unescape * and ? for glob matching
        pattern = pattern.replace(r"\*", ".*")  # * matches anything
        pattern = pattern.replace(r"\?", ".")  # ? matches single char
        return f"^{pattern}$"


class RuleEngine:
    """Rule-based file matching and profile assignment."""

    def __init__(self, rules: Optional[List[Union[Rule, Dict[str, Any]]]] = None):
        """Initialize rule engine.

        Args:
            rules: List of Rule objects or rule dictionaries
        """
        # Convert dicts to Rule objects if needed
        converted_rules = []
        for rule in rules or []:
            if isinstance(rule, dict):
                # Convert dict to Rule object
                pattern_type_str = rule.get("pattern_type", "glob")
                pattern_type = (
                    PatternType(pattern_type_str)
                    if isinstance(pattern_type_str, str)
                    else pattern_type_str
                )
                converted_rules.append(
                    Rule(
                        pattern=rule["pattern"],
                        profile=rule["profile"],
                        output_pattern=rule.get("output_pattern", "{filename}"),
                        pattern_type=pattern_type,
                        delete_input=rule.get("delete_input", True),
                        priority=rule.get("priority", 100),
                    )
                )
            else:
                # Already a Rule object
                converted_rules.append(rule)

        self.rules = sorted(converted_rules, key=lambda r: r.priority, reverse=True)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule and re-sort by priority.

        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def find_matching_rule(self, filename: str) -> Optional[Rule]:
        """Find first matching rule for filename.

        Args:
            filename: Filename to match

        Returns:
            Matching Rule or None
        """
        for rule in self.rules:
            if rule.matches(filename):
                return rule
        return None

    def find_profile(self, filename: str) -> Optional[str]:
        """Find profile for filename.

        Args:
            filename: Filename to match

        Returns:
            Profile name or None
        """
        rule = self.find_matching_rule(filename)
        return rule.profile if rule else None

    def match(self, filename: str) -> Optional[Dict[str, Any]]:
        """Match filename against rules and return matching rule as dict.

        Args:
            filename: Filename to match

        Returns:
            Rule dict or None if no match
        """
        rule = self.find_matching_rule(filename)
        if not rule:
            return None
        return {
            "pattern": rule.pattern,
            "profile": rule.profile,
            "output_pattern": rule.output_pattern,
            "pattern_type": rule.pattern_type.value,
            "delete_input": rule.delete_input,
            "priority": rule.priority,
        }

    def get_output_path(self, input_path: Path, output_dir: Path) -> Optional[Path]:
        """Get output path for input file.

        Args:
            input_path: Input file path
            output_dir: Output directory

        Returns:
            Output file path or None if no matching rule
        """
        rule = self.find_matching_rule(input_path.name)
        if not rule:
            return None
        return rule.get_output_path(input_path, output_dir)

    def get_status(self) -> dict:
        """Get rule engine status.

        Returns:
            Dict with rule information
        """
        return {
            "num_rules": len(self.rules),
            "rules": [
                {
                    "pattern": r.pattern,
                    "profile": r.profile,
                    "priority": r.priority,
                    "pattern_type": r.pattern_type.value,
                }
                for r in self.rules
            ],
        }
