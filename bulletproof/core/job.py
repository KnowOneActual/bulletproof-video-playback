"""Transcode job execution and management."""

import asyncio
import json
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from bulletproof.core.profile import TranscodeProfile

SPEED_PRESET_TYPE = Literal["fast", "normal", "slow"]


@dataclass
class TranscodeJob:
    """A single transcode operation."""

    input_file: Path
    output_file: Path
    profile: TranscodeProfile
    speed_preset: SPEED_PRESET_TYPE = "normal"  # fast, normal, slow
    status: str = "pending"  # pending, running, complete, error
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    progress: float = 0.0  # 0-100
    current_frame: int = 0
    total_frames: int = 0

    def __post_init__(self):
        """Validate inputs."""
        self.input_file = Path(self.input_file)
        self.output_file = Path(self.output_file)

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

        if self.speed_preset not in ["fast", "normal", "slow"]:
            raise ValueError(f"Invalid speed_preset: {self.speed_preset}")

    async def _get_duration(self) -> float | None:
        """Get video duration in seconds using ffprobe (async)."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(self.input_file),
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                return float(stdout.decode().strip())
        except (ValueError, FileNotFoundError, OSError):
            pass
        return None

    async def _get_framerate(self) -> float | None:
        """Get video framerate using ffprobe (async)."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(self.input_file),
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            if process.returncode == 0:
                # Parse fraction (e.g., "30000/1001" or "24/1")
                fps_str = stdout.decode().strip()
                if "/" in fps_str:
                    num, denom = fps_str.split("/")
                    return float(num) / float(denom)
                return float(fps_str)
        except (
            ValueError,
            FileNotFoundError,
            ZeroDivisionError,
            OSError,
        ):
            pass
        return None

    def _adjust_preset_for_speed(self, codec_preset: str) -> str:
        """Adjust codec preset based on speed_preset setting."""
        if self.profile.codec == "prores":
            # ProRes presets are fixed, no speed adjustment
            return codec_preset

        # For H.264 and H.265, adjust the preset
        preset_map = {
            "fast": {"fast": "fast", "medium": "fast", "slow": "medium"},
            "normal": {"fast": "fast", "medium": "medium", "slow": "slow"},
            "slow": {"fast": "medium", "medium": "slow", "slow": "slower"},
        }

        if codec_preset in preset_map[self.speed_preset]:
            return preset_map[self.speed_preset][codec_preset]
        return codec_preset

    async def _build_ffmpeg_command(self) -> list[str]:
        """Build ffmpeg command from profile with speed adjustments."""
        cmd = [
            "ffmpeg",
            "-i",
            str(self.input_file),
            "-progress",
            "pipe:1",  # Output progress to stdout
        ]

        # Video codec
        if self.profile.codec == "none":
            cmd.append("-vn")
        elif self.profile.codec == "prores":
            cmd.extend(["-c:v", "prores"])
            if self.profile.preset == "hq":
                cmd.extend(["-profile:v", "4"])  # ProRes 4444
            elif self.profile.preset == "lt":
                cmd.extend(["-profile:v", "1"])  # ProRes LT
            elif self.profile.preset == "proxy":
                cmd.extend(["-profile:v", "0"])  # ProRes Proxy
        elif self.profile.codec == "h264":
            cmd.extend(["-c:v", "libx264"])
            adjusted_preset = self._adjust_preset_for_speed(self.profile.preset)
            cmd.extend(["-preset", adjusted_preset])
            if self.profile.max_bitrate:
                cmd.extend(["-b:v", self.profile.max_bitrate])
        elif self.profile.codec == "h265":
            cmd.extend(["-c:v", "libx265"])
            adjusted_preset = self._adjust_preset_for_speed(self.profile.preset)
            cmd.extend(["-preset", adjusted_preset])

            # Use CRF mode if quality is set and no bitrate limit
            if self.profile.quality and not self.profile.max_bitrate:
                cmd.extend(["-crf", str(self.profile.quality)])
            elif self.profile.max_bitrate:
                cmd.extend(["-b:v", self.profile.max_bitrate])

            # Add compatibility tag for broader H.265 support
            if self.profile.extension == "mp4":
                cmd.extend(["-tag:v", "hvc1"])

        if self.profile.codec != "none":
            # Keyframe interval settings
            if self.profile.keyframe_interval is not None:
                # Get source framerate (or use target framerate if specified)
                fps = self.profile.frame_rate
                if not fps:
                    fps = await self._get_framerate()

                if fps:
                    # Calculate GOP size: framerate × interval in seconds
                    gop_size = int(fps * self.profile.keyframe_interval)

                    # Set GOP size (-g flag)
                    cmd.extend(["-g", str(gop_size)])

                    # Set minimum keyframe interval to same as GOP
                    cmd.extend(["-keyint_min", str(gop_size)])

                    # Force strict keyframe intervals if requested
                    if self.profile.force_keyframes:
                        # Disable scene change detection
                        cmd.extend(["-sc_threshold", "0"])

                        # Force keyframes at exact time intervals
                        interval = self.profile.keyframe_interval
                        cmd.extend(["-force_key_frames", f"expr:gte(t,n_forced*{interval})"])

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
        if getattr(self.profile, "audio_sample_rate", None):
            cmd.extend(["-ar", self.profile.audio_sample_rate])

        # Add faststart flag for MP4/MKV streaming optimization
        if self.profile.extension in ["mp4", "mkv"]:
            cmd.extend(["-movflags", "+faststart"])

        # Output file
        cmd.extend(["-y", "-loglevel", "error", str(self.output_file)])

        return cmd

    async def execute(self, progress_callback: Callable[[float], None] | None = None) -> bool:
        """Execute the transcode job asynchronously.

        Args:
            progress_callback: Optional callback receiving progress (0.0-100.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.status = "running"
            self.started_at = datetime.now().isoformat()

            # Get duration for progress calculation
            duration_seconds = await self._get_duration()
            cmd = await self._build_ffmpeg_command()

            # Run ffmpeg with live progress parsing
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Parse progress from ffmpeg output
            time_pattern = re.compile(r"out_time_ms=(\d+)")

            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                if duration_seconds:
                    time_match = time_pattern.search(line_str)
                    if time_match:
                        time_ms = int(time_match.group(1))
                        elapsed_seconds = time_ms / 1_000_000
                        self.progress = min(100.0, (elapsed_seconds / duration_seconds) * 100.0)
                        if progress_callback:
                            progress_callback(self.progress)

            # Wait for process to finish
            return_code = await process.wait()

            if return_code != 0:
                stderr = await process.stderr.read()
                self.error_message = (
                    stderr.decode().strip() or f"FFmpeg exited with code {return_code}"
                )
                self.status = "error"
                return False

            self.status = "complete"
            self.progress = 100.0
            self.completed_at = datetime.now().isoformat()
            return True

        except asyncio.CancelledError:
            self.status = "cancelled"
            self.error_message = "Transcode cancelled"
            # Attempt to kill process if still running
            try:
                process.terminate()
                await process.wait()
            except Exception:
                pass
            # Cleanup incomplete output file
            if self.output_file.exists():
                try:
                    self.output_file.unlink()
                except Exception:
                    pass
            raise
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            return False

    def sync_execute(self, show_progress: bool = True) -> bool:
        """Synchronous wrapper for execute().

        Args:
            show_progress: Whether to print a progress bar to stdout

        Returns:
            True if successful, False otherwise
        """

        def _print_bar(p: float):
            filled = int(50 * p // 100)
            bar = "█" * filled + "░" * (50 - filled)
            print(f"\rProgress: |{bar}| {p:.1f}%", end="", flush=True)

        if show_progress:
            print(f"Transcoding: {self.input_file.name}")
            callback = _print_bar
        else:
            callback = None

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        success = loop.run_until_complete(self.execute(progress_callback=callback))
        if show_progress:
            print("\n")
        return success

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["input_file"] = str(self.input_file)
        data["output_file"] = str(self.output_file)
        data["profile"] = self.profile.to_dict()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
