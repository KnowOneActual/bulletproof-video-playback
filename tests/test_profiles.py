"""Tests for profile functionality."""

import pytest
from bulletproof.core import get_profile, list_profiles, TranscodeProfile


def test_list_profiles():
    """Test that all 7 profiles are available."""
    profiles = list_profiles()
    assert len(profiles) == 7
    assert "live-qlab" in profiles
    assert "live-prores-lt" in profiles
    assert "live-h264" in profiles
    assert "standard-playback" in profiles
    assert "stream-hd" in profiles
    assert "stream-4k" in profiles
    assert "archival" in profiles


def test_get_profile_live_qlab():
    """Test live-qlab profile (ProRes Proxy for QLab)."""
    profile = get_profile("live-qlab")
    assert profile.name == "live-qlab"
    assert profile.codec == "prores"
    assert profile.preset == "proxy"  # ProRes Proxy (QLab recommended)
    assert profile.quality == 80
    assert profile.max_bitrate is None  # Lossless
    assert profile.extension == "mov"


def test_get_profile_live_prores_lt():
    """Test live-prores-lt profile."""
    profile = get_profile("live-prores-lt")
    assert profile.name == "live-prores-lt"
    assert profile.codec == "prores"
    assert profile.quality == 85
    assert profile.extension == "mov"


def test_get_profile_standard_playback():
    """Test standard-playback profile."""
    profile = get_profile("standard-playback")
    assert profile.name == "standard-playback"
    assert profile.codec == "h264"
    assert profile.quality == 85
    assert profile.extension == "mp4"


def test_get_profile_stream_hd():
    """Test stream-hd profile."""
    profile = get_profile("stream-hd")
    assert profile.name == "stream-hd"
    assert profile.codec == "h265"
    assert profile.frame_rate == 29.97
    assert profile.scale == "1920:1080"
    assert profile.extension == "mp4"


def test_get_profile_archival():
    """Test archival profile (ProRes HQ)."""
    profile = get_profile("archival")
    assert profile.name == "archival"
    assert profile.codec == "prores"
    assert profile.preset == "hq"  # ProRes HQ for archival
    assert profile.quality == 100
    assert profile.extension == "mov"


def test_get_profile_invalid():
    """Test that invalid profile raises error."""
    with pytest.raises(ValueError):
        get_profile("nonexistent-profile")


def test_profile_to_dict():
    """Test profile to_dict method."""
    profile = get_profile("live-qlab")
    data = profile.to_dict()
    assert isinstance(data, dict)
    assert "name" in data
    assert "codec" in data
    assert data["name"] == "live-qlab"


def test_profile_to_json():
    """Test profile to_json method."""
    profile = get_profile("standard-playback")
    json_str = profile.to_json()
    assert isinstance(json_str, str)
    assert "standard-playback" in json_str
    assert "h264" in json_str


def test_codec_extensions():
    """Test that codec-extension mapping is correct."""
    assert get_profile("live-qlab").extension == "mov"  # ProRes -> MOV
    assert get_profile("live-prores-lt").extension == "mov"  # ProRes -> MOV
    assert get_profile("standard-playback").extension == "mp4"  # H.264 -> MP4
    assert get_profile("stream-hd").extension == "mp4"  # H.265 -> MP4
    assert get_profile("archival").extension == "mov"  # ProRes -> MOV
