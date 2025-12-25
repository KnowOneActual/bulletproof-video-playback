"""Transcode job execution and management."""

import subprocess
import json
import re
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
    progress: float = 0.0  # 0-100
    current_frame: int = 0
    total_frames: int = 0

    def __post_init__(self):
        """Validate inputs."""
        self.input_file = Path(self.input_file)
        self.output_file = Path(self.output_file)

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

    def _get_duration(self) -> Optional[float]:
        """Get video duration in seconds using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1:noprint_wrappers=1",
                str(self.input_file),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            pass
        return None

    def _build_ffmpeg_command(self) -> list:
        """Build ffmpeg command from profile."""
        cmd = [
            "ffmpeg",
            "-i",
            str(self.input_file),
            "-progress",
            "pipe:1",  # Output progress to stdout
        ]

        # Video codec
        if self.profile.codec == "prores":
            cmd.extend(["-c:v", "prores"])
            if self.profile.preset == "hq":
                cmd.extend(["-profile:v", "4"])  # ProRes 4444
            elif self.profile.preset == "lt":
                cmd.extend(["-profile:v", "1"])  # ProRes LT
            elif self.profile.preset == "proxy":
                cmd.extend(["-profile:v", "0"])  # ProRes Proxy
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

        # Output file (quiet stderr to avoid clutter)
        cmd.extend(["-y", "-loglevel", "error", str(self.output_file)])

        return cmd

    def _print_progress_bar(
        self, current: int, total: int, prefix: str = "", decimals: int = 1
    ):
        """Print a simple progress bar to terminal."""
        if total <= 0:
            return

        percent = 100 * (current / float(total))
        filled_length = int(50 * current // total)
        bar = "█" * filled_length + "░" * (50 - filled_length)

        print(
            f"\r{prefix} |{bar}| {percent:.1f}% ({current}/{total})",
            end="",
            flush=True,
        )

    def execute(self, show_progress: bool = True) -> bool:
        """Execute the transcode job with real-time progress.

        Args:
            show_progress: Show progress bar during transcoding

        Returns:
            True if successful, False otherwise
        """
        try:
            self.status = "running"
            self.started_at = datetime.now().isoformat()

            # Get duration for progress calculation
            duration_seconds = self._get_duration()

            cmd = self._build_ffmpeg_command()

            if show_progress and duration_seconds:
                print(f"\nTranscoding: {self.input_file.name}")
                print(f"Duration: {duration_seconds / 60:.1f} minutes\n")

            # Run ffmpeg with live progress parsing
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Parse progress from ffmpeg output
            frame_pattern = re.compile(r"frame=(\d+)")
            time_pattern = re.compile(r"out_time_ms=(\d+)")

            for line in process.stdout:
                if show_progress and duration_seconds:
                    # Try to extract time progress
                    time_match = time_pattern.search(line)
                    if time_match:
                        time_ms = int(time_match.group(1))
                        elapsed_seconds = time_ms / 1_000_000
                        progress = min(
                            100, (elapsed_seconds / duration_seconds) * 100
                        )
                        self.progress = progress
                        self._print_progress_bar(
                            int(elapsed_seconds),
                            int(duration_seconds),
                            prefix="Progress:",
                        )

            # Wait for process to finish
            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read() if process.stderr else ""
                raise subprocess.CalledProcessError(
                    process.returncode, cmd, stderr=stderr
                )

            if show_progress:
                print("\n")  # New line after progress bar

            self.status = "complete"
            self.progress = 100.0
            self.completed_at = datetime.now().isoformat()
            return True

        except subprocess.CalledProcessError as e:
            self.status = "error"
            self.error_message = (
                e.stderr if isinstance(e.stderr, str) else str(e.stderr)
            )
            if "ffmpeg" in self.error_message.lower():
                print(f"\n✗ FFmpeg error: {self.error_message[:200]}")
            return False
        except KeyboardInterrupt:
            self.status = "cancelled"
            self.error_message = "User cancelled transcode (Ctrl+C)"
            print("\n\n✗ Transcode cancelled by user")
            # Cleanup incomplete output file
            if self.output_file.exists():
                try:
                    self.output_file.unlink()
                except Exception:
                    pass
            return False
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            print(f"\n✗ Error: {self.error_message}")
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
