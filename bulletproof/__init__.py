"""bulletproof-video-playback: Professional video transcoding for theater & streaming."""

__version__ = "0.1.0"
__author__ = "Beau Bremer"
__email__ = "dev@knowoneactual.com"

from bulletproof.core import TranscodeProfile, TranscodeJob, get_profile, list_profiles
from bulletproof.cli import cli

__all__ = [
    "__version__",
    "TranscodeProfile",
    "TranscodeJob",
    "get_profile",
    "list_profiles",
    "cli",
]
