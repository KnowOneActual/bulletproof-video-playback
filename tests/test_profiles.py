"""Tests for profile functionality."""

import pytest
from bulletproof.core import get_profile, list_profiles, TranscodeProfile


def test_list_profiles():
    """Test that all 7 profiles are available."""
    profiles = list_profiles()
    assert len(profiles) == 7
    assert "theater-qlab" in profiles
    assert "theater-prores-lt" in profiles
    assert "theater-h264" in profiles
    assert "standard-playback" in profiles
    assert "stream-hd" in profiles
    assert "stream-4k" in profiles
    assert "archival" in profiles


def test_get_profile_theater_qlab():
    """Test theater-qlab profile."""
    profile = get_profile("theater-qlab")
    assert profile.name == "theater-qlab"
    assert profile.codec == "prores"
    assert profile.preset == "hq"
    assert profile.quality == 100
    assert profile.max_bitrate is None  # Lossless


def test_get_profile_standard_playback():
    """Test standard-playback profile."""
    profile = get_profile("standard-playback")
    assert profile.name == "standard-playback"
    assert profile.codec == "h264"
    assert profile.quality == 85


def test_get_profile_stream_hd():
    """Test stream-hd profile."""
    profile = get_profile("stream-hd")
    assert profile.name == "stream-hd"
    assert profile.codec == "h265"
    assert profile.frame_rate == 29.97
    assert profile.scale == "1920:1080"


def test_get_profile_invalid():
    """Test that invalid profile raises error."""
    with pytest.raises(ValueError):
        get_profile("nonexistent-profile")


def test_profile_to_dict():
    """Test profile to_dict method."""
    profile = get_profile("theater-qlab")
    data = profile.to_dict()
    assert isinstance(data, dict)
    assert "name" in data
    assert "codec" in data
    assert data["name"] == "theater-qlab"


def test_profile_to_json():
    """Test profile to_json method."""
    profile = get_profile("standard-playback")
    json_str = profile.to_json()
    assert isinstance(json_str, str)
    assert "standard-playback" in json_str
    assert "h264" in json_str
