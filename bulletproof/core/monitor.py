"""File system monitoring for video transcode workflows."""

import os
from pathlib import Path
from typing import Set, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


# Common video file extensions
VIDEO_EXTENSIONS = {
    ".mov",
    ".mp4",
    ".mxf",
    ".avi",
    ".mkv",
    ".flv",
    ".wmv",
    ".webm",
    ".m2ts",
    ".mts",
    ".ts",
    ".m4v",
    ".3gp",
    ".3g2",
    ".qt",
    ".dv",
    ".dvr",
    ".asf",
}


@dataclass
class FileInfo:
    """Information about a monitored file."""

    path: Path
    size: int
    mtime: float  # modification time
    hash: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    processing: bool = False
    processed: bool = False

    def __post_init__(self):
        """Calculate hash if not provided."""
        if not self.hash:
            self.hash = hashlib.sha256(str(self.path).encode()).hexdigest()[:16]


class FolderMonitor:
    """Monitor a folder for new video files.

    Watches a directory, detects video files, and tracks their state.
    Useful for automated transcode workflows.
    """

    def __init__(
        self,
        watch_path: Path,
        extensions: Optional[Set[str]] = None,
        on_file_detected: Optional[Callable[[FileInfo], None]] = None,
    ):
        """Initialize folder monitor.

        Args:
            watch_path: Directory to monitor
            extensions: Video file extensions to detect (defaults to VIDEO_EXTENSIONS)
            on_file_detected: Callback when new file is detected
        """
        self.watch_path = Path(watch_path)
        if not self.watch_path.exists():
            raise FileNotFoundError(f"Watch path does not exist: {self.watch_path}")
        if not self.watch_path.is_dir():
            raise NotADirectoryError(
                f"Watch path is not a directory: {self.watch_path}"
            )

        self.extensions = extensions or VIDEO_EXTENSIONS
        self.on_file_detected = on_file_detected

        # Track known files to avoid duplicate detection
        self._known_files: dict[str, FileInfo] = {}  # hash -> FileInfo
        self._stable_files: Set[str] = set()  # hashes of stable (not changing) files

    def scan(self) -> list[FileInfo]:
        """Scan directory for video files.

        Returns:
            List of newly detected FileInfo objects
        """
        detected = []

        try:
            for entry in self.watch_path.iterdir():
                if not entry.is_file():
                    continue

                # Check if file has video extension (case-insensitive)
                if entry.suffix.lower() not in self.extensions:
                    continue

                # Get file info
                try:
                    stat = entry.stat()
                    file_info = FileInfo(
                        path=entry,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                    )
                except (OSError, FileNotFoundError):
                    # File may have been deleted or is inaccessible
                    continue

                # Check if we've seen this file before
                if file_info.hash in self._known_files:
                    # File is known - check if it's stable
                    prev_info = self._known_files[file_info.hash]
                    if (
                        prev_info.size == file_info.size
                        and prev_info.mtime == file_info.mtime
                    ):
                        # File hasn't changed, it's stable
                        self._stable_files.add(file_info.hash)
                    else:
                        # File is still changing, update it
                        file_info.detected_at = prev_info.detected_at
                        self._known_files[file_info.hash] = file_info
                else:
                    # New file detected
                    self._known_files[file_info.hash] = file_info
                    detected.append(file_info)

                    # Call callback if provided
                    if self.on_file_detected:
                        self.on_file_detected(file_info)

        except (OSError, PermissionError) as e:
            # Directory may be inaccessible
            print(f"Error scanning directory {self.watch_path}: {e}")

        return detected

    def get_stable_files(self) -> list[FileInfo]:
        """Get list of stable (not changing) files ready for processing.

        Returns:
            List of FileInfo objects for stable files
        """
        return [
            info
            for hash_val, info in self._known_files.items()
            if hash_val in self._stable_files
            and not info.processing
            and not info.processed
        ]

    def mark_processing(self, file_info: FileInfo) -> None:
        """Mark a file as being processed.

        Args:
            file_info: FileInfo to mark
        """
        file_info.processing = True
        self._known_files[file_info.hash] = file_info

    def mark_processed(self, file_info: FileInfo) -> None:
        """Mark a file as successfully processed.

        Args:
            file_info: FileInfo to mark
        """
        file_info.processing = False
        file_info.processed = True
        self._known_files[file_info.hash] = file_info

    def mark_error(self, file_info: FileInfo) -> None:
        """Mark a file as having processing error.

        Args:
            file_info: FileInfo to mark
        """
        file_info.processing = False
        self._known_files[file_info.hash] = file_info

    def clear_processed(self) -> None:
        """Clear processed files from tracking (optional cleanup)."""
        self._known_files = {
            hash_val: info
            for hash_val, info in self._known_files.items()
            if not info.processed
        }
        self._stable_files = {
            hash_val
            for hash_val in self._stable_files
            if hash_val in self._known_files
        }

    def get_status(self) -> dict:
        """Get current monitoring status.

        Returns:
            Dict with status information
        """
        pending = sum(1 for info in self._known_files.values() if not info.processed)
        processing = sum(1 for info in self._known_files.values() if info.processing)
        processed = sum(1 for info in self._known_files.values() if info.processed)

        return {
            "watch_path": str(self.watch_path),
            "total_files": len(self._known_files),
            "pending": pending,
            "processing": processing,
            "processed": processed,
            "known_files": {
                hash_val: {
                    "path": str(info.path.name),
                    "size": info.size,
                    "status": (
                        "processed"
                        if info.processed
                        else "processing"
                        if info.processing
                        else "pending"
                    ),
                    "detected_at": info.detected_at.isoformat(),
                }
                for hash_val, info in self._known_files.items()
            },
        }
