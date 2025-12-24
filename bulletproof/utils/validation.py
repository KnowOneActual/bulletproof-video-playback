"""Validation utilities."""

from pathlib import Path


def validate_input_file(file_path: str) -> bool:
    """Validate that input file exists and is readable."""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_output_path(file_path: str) -> bool:
    """Validate that output path is writable."""
    try:
        path = Path(file_path)
        parent = path.parent
        return parent.exists() or parent == Path()
    except Exception:
        return False


def validate_profile_name(name: str) -> bool:
    """Validate profile name format."""
    return (
        isinstance(name, str)
        and len(name) > 0
        and (name.replace("-", "").replace("_", "").isalnum())
    )


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0
