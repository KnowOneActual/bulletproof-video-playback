"""Tests for validation utilities."""

import pytest
from pathlib import Path
from bulletproof.utils import (
    validate_input_file,
    validate_output_path,
    validate_profile_name,
    get_file_size_mb,
)


def test_validate_input_file_nonexistent():
    """Test validation of nonexistent file."""
    assert not validate_input_file("/nonexistent/file.mov")


def test_validate_input_file_exists(tmp_path):
    """Test validation of existing file."""
    test_file = tmp_path / "test.mov"
    test_file.write_text("test")
    assert validate_input_file(str(test_file))


def test_validate_output_path_valid():
    """Test validation of valid output path."""
    assert validate_output_path("/tmp/output.mov")


def test_validate_output_path_current_dir():
    """Test validation of output in current directory."""
    assert validate_output_path("output.mov")


def test_validate_profile_name_valid():
    """Test valid profile names."""
    assert validate_profile_name("theater-qlab")
    assert validate_profile_name("standard_playback")
    assert validate_profile_name("profile123")


def test_validate_profile_name_invalid():
    """Test invalid profile names."""
    assert not validate_profile_name("")
    assert not validate_profile_name("profile!invalid")


def test_get_file_size_mb_nonexistent():
    """Test file size of nonexistent file."""
    assert get_file_size_mb("/nonexistent/file.mov") == 0.0


def test_get_file_size_mb_exists(tmp_path):
    """Test file size of existing file."""
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"x" * 1024 * 1024)  # 1 MB
    size = get_file_size_mb(str(test_file))
    assert 0.99 < size < 1.01  # ~1 MB
