"""bulletproof-video-playback: Professional video transcoding for theater & streaming."""

__version__ = "3.0.0"
__author__ = "Beau Bremer"
__email__ = "dev@knowoneactual.com"

from bulletproof.cli import cli
from bulletproof.core import TranscodeJob, TranscodeProfile, get_profile, list_profiles

__all__ = [
    "__version__",
    "TranscodeProfile",
    "TranscodeJob",
    "get_profile",
    "list_profiles",
    "cli",
]
