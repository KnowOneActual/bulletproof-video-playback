"""Transcode job execution and management."""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from bulletproof.core.profile import TranscodeProfile


@dataclass
class TranscodeJob:
    """A single transcode operation."""

    input_file: Path
    output_file: Path
    profile: TranscodeProfile
    status: str = "pending"  # pending, running, complete, error
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate inputs."""
        self.input_file = Path(self.input_file)
        self.output_file = Path(self.output_file)

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

    def _build_ffmpeg_command(self) -> list:
        """Build ffmpeg command from profile."""
        cmd = ["ffmpeg", "-i", str(self.input_file)]

        # Video codec
        if self.profile.codec == "prores":
            cmd.extend(["-c:v", "prores"])
            if self.profile.preset == "hq":
                cmd.extend(["-profile:v", "4"])  # ProRes 4444
            elif self.profile.preset == "lt":
                cmd.extend(["-profile:v", "1"])  # ProRes LT
        elif self.profile.codec == "h264":
            cmd.extend(["-c:v", "libx264", "-preset", self.profile.preset])
            if self.profile.max_bitrate:
                cmd.extend(["-b:v", self.profile.max_bitrate])
        elif self.profile.codec == "h265":
            cmd.extend(["-c:v", "libx265", "-preset", self.profile.preset])
            if self.profile.max_bitrate:
                cmd.extend(["-b:v", self.profile.max_bitrate])

        # Pixel format
        if self.profile.pixel_format:
            cmd.extend(["-pix_fmt", self.profile.pixel_format])

        # Frame rate
        if self.profile.frame_rate:
            cmd.extend(["-r", str(self.profile.frame_rate)])

        # Scale
        if self.profile.scale:
            cmd.extend(["-vf", f"scale={self.profile.scale}"])

        # Audio codec
        cmd.extend(["-c:a", self.profile.audio_codec])
        if self.profile.audio_bitrate != "0":
            cmd.extend(["-b:a", self.profile.audio_bitrate])

        # Output file
        cmd.append(str(self.output_file))

        return cmd

    def execute(self) -> bool:
        """Execute the transcode job."""
        try:
            self.status = "running"
            self.started_at = datetime.now().isoformat()

            cmd = self._build_ffmpeg_command()
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            self.status = "complete"
            self.completed_at = datetime.now().isoformat()
            return True

        except subprocess.CalledProcessError as e:
            self.status = "error"
            self.error_message = e.stderr
            return False
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["input_file"] = str(self.input_file)
        data["output_file"] = str(self.output_file)
        data["profile"] = self.profile.to_dict()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
