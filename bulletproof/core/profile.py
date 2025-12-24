"""Transcode profile definitions and management."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json


@dataclass
class TranscodeProfile:
    """Video transcode profile configuration."""

    name: str
    codec: str  # prores, h264, h265, vp9, etc.
    preset: str  # hq, lq, lt, etc. (codec-specific)
    quality: int  # 0-100 (quality percentage)
    max_bitrate: Optional[str]  # e.g., "50M", None for lossless
    frame_rate: Optional[float]  # e.g., 23.976, 30, None for source
    pixel_format: Optional[str]  # e.g., yuv420p, none (preserve source)
    scale: Optional[str]  # e.g., "1920:1080", None for source
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# Built-in profiles
BUILT_IN_PROFILES = {
    "live-qlab": TranscodeProfile(
        name="live-qlab",
        codec="prores",
        preset="hq",
        quality=100,
        max_bitrate=None,
        frame_rate=None,
        pixel_format="yuv422p10le",
        scale=None,
        audio_codec="pcm_s24le",
        audio_bitrate="0",
        description="ProRes HQ for QLab on macOS (best quality, largest files)",
    ),
    "live-prores-lt": TranscodeProfile(
        name="live-prores-lt",
        codec="prores",
        preset="lt",
        quality=85,
        max_bitrate=None,
        frame_rate=None,
        pixel_format="yuv422p10le",
        scale=None,
        audio_codec="pcm_s24le",
        audio_bitrate="0",
        description="ProRes LT for live playback (reduced file size, good quality)",
    ),
    "live-h264": TranscodeProfile(
        name="live-h264",
        codec="h264",
        preset="slow",
        quality=95,
        max_bitrate="100M",
        frame_rate=None,
        pixel_format="yuv420p",
        scale=None,
        description="H.264 for cross-platform live playback",
    ),
    "standard-playback": TranscodeProfile(
        name="standard-playback",
        codec="h264",
        preset="medium",
        quality=85,
        max_bitrate="20M",
        frame_rate=None,
        pixel_format="yuv420p",
        scale=None,
        description="H.264 for Miccia Player, VLC, general use",
    ),
    "stream-hd": TranscodeProfile(
        name="stream-hd",
        codec="h265",
        preset="medium",
        quality=80,
        max_bitrate="8M",
        frame_rate=29.97,
        pixel_format="yuv420p",
        scale="1920:1080",
        description="H.265 for streaming (1080p, efficient)",
    ),
    "stream-4k": TranscodeProfile(
        name="stream-4k",
        codec="h265",
        preset="medium",
        quality=85,
        max_bitrate="25M",
        frame_rate=29.97,
        pixel_format="yuv420p",
        scale="3840:2160",
        description="H.265 for 4K streaming",
    ),
    "archival": TranscodeProfile(
        name="archival",
        codec="prores",
        preset="hq",
        quality=100,
        max_bitrate=None,
        frame_rate=None,
        pixel_format="yuv422p10le",
        scale=None,
        audio_codec="pcm_s24le",
        audio_bitrate="0",
        description="ProRes HQ for long-term archival storage",
    ),
}


def get_profile(name: str) -> TranscodeProfile:
    """Get a profile by name."""
    if name not in BUILT_IN_PROFILES:
        raise ValueError(f"Profile '{name}' not found. Available: {list(BUILT_IN_PROFILES.keys())}")
    return BUILT_IN_PROFILES[name]


def list_profiles() -> Dict[str, TranscodeProfile]:
    """List all available profiles."""
    return BUILT_IN_PROFILES.copy()
