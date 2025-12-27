"""Transcode job queue with persistence."""

import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from bulletproof.core.monitor import FileInfo
from bulletproof.core.profile import TranscodeProfile


class JobStatus(str, Enum):
    """Job processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class QueuedJob:
    """A job in the transcode queue."""

    input_file: Path
    output_file: Path
    profile_name: str
    status: JobStatus = JobStatus.PENDING
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Set created_at if not provided."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        # Ensure paths are Path objects
        self.input_file = Path(self.input_file)
        self.output_file = Path(self.output_file)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "input_file": str(self.input_file),
            "output_file": str(self.output_file),
            "profile_name": self.profile_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QueuedJob":
        """Create from dictionary (e.g., from JSON)."""
        return cls(
            input_file=Path(data["input_file"]),
            output_file=Path(data["output_file"]),
            profile_name=data["profile_name"],
            status=JobStatus(data.get("status", "pending")),
            created_at=data.get("created_at", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
        )


class TranscodeQueue:
    """In-memory queue with optional JSON persistence."""

    def __init__(self, persist_path: Optional[Path] = None):
        """Initialize queue.

        Args:
            persist_path: Optional path to persist queue state to JSON
        """
        self.persist_path = Path(persist_path) if persist_path else None
        self._jobs: List[QueuedJob] = []
        self._history: List[QueuedJob] = []

        # Load persisted queue if path provided
        if self.persist_path and self.persist_path.exists():
            self._load()

    def add(self, job: QueuedJob) -> None:
        """Add job to queue.

        Args:
            job: QueuedJob to add
        """
        self._jobs.append(job)
        self._save()

    def add_from_file(self, file_info: FileInfo, output_file: Path, profile_name: str) -> QueuedJob:
        """Create and add job from FileInfo.

        Args:
            file_info: FileInfo from FolderMonitor
            output_file: Output file path
            profile_name: Name of profile to use

        Returns:
            The created QueuedJob
        """
        job = QueuedJob(
            input_file=file_info.path,
            output_file=output_file,
            profile_name=profile_name,
        )
        self.add(job)
        return job

    def get_pending(self) -> Optional[QueuedJob]:
        """Get next pending job without removing it.

        Returns:
            First pending QueuedJob or None
        """
        for job in self._jobs:
            if job.status == JobStatus.PENDING:
                return job
        return None

    def get_next(self) -> Optional[QueuedJob]:
        """Get and remove next pending job.

        Returns:
            First pending QueuedJob or None
        """
        job = self.get_pending()
        if job:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now().isoformat()
            self._save()
        return job

    def mark_complete(self, job: QueuedJob) -> None:
        """Mark job as complete.

        Args:
            job: QueuedJob to mark complete
        """
        job.status = JobStatus.COMPLETE
        job.completed_at = datetime.now().isoformat()
        self._history.append(job)
        self._jobs.remove(job)
        self._save()

    def mark_error(self, job: QueuedJob, error_message: str) -> None:
        """Mark job as errored.

        Args:
            job: QueuedJob with error
            error_message: Error message
        """
        job.status = JobStatus.ERROR
        job.error_message = error_message
        job.completed_at = datetime.now().isoformat()
        self._history.append(job)
        self._jobs.remove(job)
        self._save()

    def remove(self, job: QueuedJob) -> None:
        """Remove job from queue.

        Args:
            job: QueuedJob to remove
        """
        if job in self._jobs:
            self._jobs.remove(job)
            self._save()

    def get_status(self) -> dict:
        """Get queue status.

        Returns:
            Dict with queue statistics
        """
        return {
            "pending": sum(1 for j in self._jobs if j.status == JobStatus.PENDING),
            "processing": sum(1 for j in self._jobs if j.status == JobStatus.PROCESSING),
            "total_queued": len(self._jobs),
            "completed": sum(1 for j in self._history if j.status == JobStatus.COMPLETE),
            "errored": sum(1 for j in self._history if j.status == JobStatus.ERROR),
            "total_processed": len(self._history),
        }

    def get_all(self) -> list[QueuedJob]:
        """Get all jobs in queue.

        Returns:
            List of all QueuedJob objects
        """
        return self._jobs.copy()

    def get_history(self, limit: Optional[int] = None) -> list[QueuedJob]:
        """Get processing history.

        Args:
            limit: Maximum number of history items to return

        Returns:
            List of processed QueuedJob objects
        """
        if limit:
            return self._history[-limit:]
        return self._history.copy()

    def _save(self) -> None:
        """Persist queue to JSON file."""
        if not self.persist_path:
            return

        # Ensure parent directory exists
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "queued": [job.to_dict() for job in self._jobs],
            "history": [job.to_dict() for job in self._history],
            "saved_at": datetime.now().isoformat(),
        }

        try:
            with open(self.persist_path, "w") as f:
                json.dump(data, f, indent=2)
        except (IOError, OSError) as e:
            print(f"Error saving queue to {self.persist_path}: {e}")

    def _load(self) -> None:
        """Load queue from JSON file."""
        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)

            # Load queued jobs
            for job_data in data.get("queued", []):
                self._jobs.append(QueuedJob.from_dict(job_data))

            # Load history
            for job_data in data.get("history", []):
                self._history.append(QueuedJob.from_dict(job_data))
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Error loading queue from {self.persist_path}: {e}")
