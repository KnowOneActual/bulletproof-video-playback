"""Data models for API responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


class FileStatus(str, Enum):
    """File monitoring status."""

    DETECTED = "detected"
    STABLE = "stable"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class JobResponse(BaseModel):
    """Single transcode job response."""

    id: str
    input_file: str
    output_file: str
    profile_name: str
    status: JobStatus
    priority: int = 100
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    progress: float = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job_123",
                "input_file": "/incoming/video.mov",
                "output_file": "/output/video_qlab.mov",
                "profile_name": "live-qlab",
                "status": "processing",
                "priority": 100,
                "created_at": "2026-02-10T17:00:00",
                "started_at": "2026-02-10T17:00:05",
                "completed_at": None,
                "error_message": None,
                "progress": 45.5,
            }
        }


class QueueStatusResponse(BaseModel):
    """Queue status response."""

    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    complete_jobs: int
    error_jobs: int
    current_job: Optional[JobResponse] = None
    jobs: List[JobResponse] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "total_jobs": 10,
                "pending_jobs": 3,
                "processing_jobs": 1,
                "complete_jobs": 5,
                "error_jobs": 1,
                "current_job": {
                    "id": "job_123",
                    "input_file": "/incoming/video.mov",
                    "output_file": "/output/video_qlab.mov",
                    "profile_name": "live-qlab",
                    "status": "processing",
                    "priority": 100,
                    "progress": 45.5,
                },
                "jobs": [],
            }
        }


class MonitorStatusResponse(BaseModel):
    """Monitor service status response."""

    running: bool
    watch_directory: str
    output_directory: str
    poll_interval: int
    timestamp: str
    detected_files: int = 0
    stable_files: int = 0
    processing_files: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "running": True,
                "watch_directory": "/incoming",
                "output_directory": "/output",
                "poll_interval": 5,
                "timestamp": "2026-02-10T17:00:00",
                "detected_files": 2,
                "stable_files": 1,
                "processing_files": 1,
            }
        }


class RuleResponse(BaseModel):
    """Rule configuration response."""

    pattern: str
    profile: str
    output_pattern: str
    pattern_type: str
    priority: int
    delete_input: bool

    class Config:
        json_schema_extra = {
            "example": {
                "pattern": "*_live.mov",
                "profile": "live-qlab",
                "output_pattern": "{filename_no_ext}_qlab.mov",
                "pattern_type": "glob",
                "priority": 100,
                "delete_input": True,
            }
        }


class HistoryResponse(BaseModel):
    """Processing history response."""

    total_processed: int
    successful: int
    failed: int
    jobs: List[JobResponse] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "total_processed": 100,
                "successful": 95,
                "failed": 5,
                "jobs": [],
            }
        }


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str  # "status", "job_update", "error", "ping"
    timestamp: str
    data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "job_update",
                "timestamp": "2026-02-10T17:00:00",
                "data": {
                    "job_id": "job_123",
                    "status": "processing",
                    "progress": 45.5,
                },
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Job not found",
                "detail": "No job with ID 'job_999' exists",
                "timestamp": "2026-02-10T17:00:00",
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "3.1.0"
    uptime_seconds: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-10T17:00:00",
                "version": "3.1.0",
                "uptime_seconds": 3600.5,
            }
        }
