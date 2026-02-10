"""API routes for monitor service."""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from bulletproof.api.models import (
    ErrorResponse,
    HealthResponse,
    HistoryResponse,
    JobResponse,
    JobStatus,
    MonitorStatusResponse,
    QueueStatusResponse,
    RuleResponse,
    WebSocketMessage,
)

# Router for all API endpoints
router = APIRouter()

# Global reference to MonitorService (set by server.py)
_monitor_service = None


def set_monitor_service(service):
    """Set the global monitor service instance."""
    global _monitor_service
    _monitor_service = service


def get_monitor_service():
    """Get the monitor service or raise error if not available."""
    if _monitor_service is None:
        raise HTTPException(status_code=503, detail="Monitor service not available")
    return _monitor_service


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint.

    Returns:
        Health status and basic system info
    """
    # Calculate uptime if service is running
    uptime = None
    if _monitor_service and hasattr(_monitor_service, "_start_time"):
        uptime = (datetime.now() - _monitor_service._start_time).total_seconds()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="3.1.0",
        uptime_seconds=uptime,
    )


@router.get("/status", response_model=MonitorStatusResponse, tags=["Monitor"])
async def get_status():
    """Get current monitor service status.

    Returns:
        Monitor status including watch directory, detected files, etc.
    """
    service = get_monitor_service()
    status = service.get_status()

    # Extract monitor-specific stats
    monitor_status = status.get("monitor", {})

    return MonitorStatusResponse(
        running=status["running"],
        watch_directory=status["watch_directory"],
        output_directory=status["output_directory"],
        poll_interval=status["poll_interval"],
        timestamp=status["timestamp"],
        detected_files=len(monitor_status.get("files", [])),
        stable_files=len(
            [f for f in monitor_status.get("files", []) if f.get("status") == "stable"]
        ),
        processing_files=len(
            [f for f in monitor_status.get("files", []) if f.get("status") == "processing"]
        ),
    )


@router.get("/queue", response_model=QueueStatusResponse, tags=["Queue"])
async def get_queue():
    """Get current queue status.

    Returns:
        Queue status with job counts and current processing job
    """
    service = get_monitor_service()
    status = service.get_status()
    queue_status = status.get("queue", {})

    # Get current processing job
    current_job = None
    processing_job = service.queue.get_current()
    if processing_job:
        current_job = JobResponse(
            id=processing_job.id,
            input_file=str(processing_job.input_file),
            output_file=str(processing_job.output_file),
            profile_name=processing_job.profile_name,
            status=JobStatus(processing_job.status),
            priority=processing_job.priority,
            created_at=processing_job.created_at,
            started_at=processing_job.started_at,
            completed_at=processing_job.completed_at,
            error_message=processing_job.error_message,
            progress=processing_job.progress,
        )

    # Get all jobs
    all_jobs = service.queue.get_all()
    jobs = [
        JobResponse(
            id=job.id,
            input_file=str(job.input_file),
            output_file=str(job.output_file),
            profile_name=job.profile_name,
            status=JobStatus(job.status),
            priority=job.priority,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            progress=job.progress,
        )
        for job in all_jobs
    ]

    return QueueStatusResponse(
        total_jobs=queue_status.get("total_jobs", 0),
        pending_jobs=queue_status.get("pending", 0),
        processing_jobs=queue_status.get("processing", 0),
        complete_jobs=queue_status.get("complete", 0),
        error_jobs=queue_status.get("error", 0),
        current_job=current_job,
        jobs=jobs,
    )


@router.get("/history", response_model=HistoryResponse, tags=["History"])
async def get_history(limit: int = 10):
    """Get processing history.

    Args:
        limit: Number of recent jobs to return (default 10)

    Returns:
        Processing history with success/failure counts
    """
    service = get_monitor_service()
    history = service.get_history(limit=limit)

    jobs = [
        JobResponse(
            id=job["id"],
            input_file=job["input_file"],
            output_file=job["output_file"],
            profile_name=job["profile_name"],
            status=JobStatus(job["status"]),
            priority=job.get("priority", 100),
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            error_message=job.get("error_message"),
            progress=job.get("progress", 0.0),
        )
        for job in history
    ]

    successful = len([j for j in jobs if j.status == JobStatus.COMPLETE])
    failed = len([j for j in jobs if j.status == JobStatus.ERROR])

    return HistoryResponse(
        total_processed=len(jobs),
        successful=successful,
        failed=failed,
        jobs=jobs,
    )


@router.get("/rules", response_model=list[RuleResponse], tags=["Configuration"])
async def get_rules():
    """Get current rule configuration.

    Returns:
        List of active rules
    """
    service = get_monitor_service()
    rule_status = service.rule_engine.get_status()

    return [
        RuleResponse(
            pattern=rule["pattern"],
            profile=rule["profile"],
            output_pattern=rule.get("output_pattern", "{filename}"),
            pattern_type=rule["pattern_type"],
            priority=rule["priority"],
            delete_input=rule.get("delete_input", True),
        )
        for rule in rule_status["rules"]
    ]


@router.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str):
    """Get specific job details.

    Args:
        job_id: Job ID to retrieve

    Returns:
        Job details
    """
    service = get_monitor_service()
    job = service.queue.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return JobResponse(
        id=job.id,
        input_file=str(job.input_file),
        output_file=str(job.output_file),
        profile_name=job.profile_name,
        status=JobStatus(job.status),
        priority=job.priority,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        progress=job.progress,
    )


# WebSocket endpoint for real-time updates
@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates.

    Sends periodic status updates to connected clients.
    """
    await websocket.accept()
    service = get_monitor_service()

    try:
        while True:
            # Get current status
            status = service.get_status()
            queue_status = status.get("queue", {})

            # Send status update
            message = WebSocketMessage(
                type="status",
                timestamp=datetime.now().isoformat(),
                data={
                    "running": status["running"],
                    "pending_jobs": queue_status.get("pending", 0),
                    "processing_jobs": queue_status.get("processing", 0),
                    "complete_jobs": queue_status.get("complete", 0),
                    "error_jobs": queue_status.get("error", 0),
                },
            )
            await websocket.send_json(message.model_dump())

            # Wait before next update
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_msg = WebSocketMessage(
            type="error",
            timestamp=datetime.now().isoformat(),
            data={"error": str(e)},
        )
        try:
            await websocket.send_json(error_msg.model_dump())
        except:
            pass
