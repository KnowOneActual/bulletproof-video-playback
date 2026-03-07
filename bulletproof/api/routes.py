"""API routes for monitor service."""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from bulletproof.api.models import (
    ConfigResponse,
    ConfigUpdate,
    HealthResponse,
    HistoryResponse,
    JobResponse,
    JobStatus,
    MonitorStatusResponse,
    ProfileResponse,
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
        paused=status.get("paused", False),
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


@router.post("/queue/pause", tags=["Queue"])
async def pause_queue():
    """Pause transcode queue processing."""
    service = get_monitor_service()
    service.pause()
    return {"message": "Queue paused"}


@router.post("/queue/resume", tags=["Queue"])
async def resume_queue():
    """Resume transcode queue processing."""
    service = get_monitor_service()
    service.resume()
    return {"message": "Queue resumed"}


@router.post("/queue/clear", tags=["Queue"])
async def clear_queue():
    """Clear all pending jobs from the queue."""
    service = get_monitor_service()
    service.clear_queue()
    return {"message": "Queue cleared"}


@router.post("/jobs/{job_id}/cancel", tags=["Jobs"])
async def cancel_job(job_id: str):
    """Cancel a pending job."""
    service = get_monitor_service()
    success = service.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Job '{job_id}' could not be cancelled (not found or not pending)",
        )

    return {"message": f"Job '{job_id}' cancelled"}


@router.post("/jobs/{job_id}/retry", tags=["Jobs"])
async def retry_job(job_id: str):
    """Retry a failed or completed job."""
    service = get_monitor_service()
    success = service.retry_job(job_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )

    return {"message": f"Job '{job_id}' retried"}


@router.get("/queue", response_model=QueueStatusResponse, tags=["Queue"])
async def get_queue():
    """Get current queue status."""
    service = get_monitor_service()
    status = service.get_status()
    queue_status = status.get("queue", {})

    # Get current processing job
    current_job = None
    processing_job = service.queue.get_current()
    if processing_job:
        current_job = JobResponse.from_queued_job(processing_job)

    # Get all jobs
    all_jobs = service.queue.get_all()
    jobs = [JobResponse.from_queued_job(job) for job in all_jobs]

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
    """Get processing history."""
    service = get_monitor_service()
    history_jobs = service.queue.get_history(limit=limit)

    # Convert history jobs (they are already in a list of QueuedJob or dict?)
    # Wait, MonitorService.get_history returns [job.to_dict() for job in jobs]
    # Let's fix MonitorService to return objects instead, or use to_dict here

    # Actually, service.queue.get_history returns QueuedJob objects if we use it directly
    jobs = [JobResponse.from_queued_job(job) for job in history_jobs]

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
    """Get current rule configuration."""
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


@router.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config():
    """Get current service configuration."""
    service = get_monitor_service()
    config = service.config

    return ConfigResponse(
        watch_directory=str(config.watch_directory),
        output_directory=str(config.output_directory),
        poll_interval=config.poll_interval,
        delete_input=config.delete_input,
        log_level=config.log_level,
        log_file=str(config.log_file) if config.log_file else None,
        persist_path=str(config.persist_path) if config.persist_path else None,
        rules=[
            RuleResponse(
                pattern=r["pattern"],
                profile=r["profile"],
                output_pattern=r.get("output_pattern", "{filename}"),
                pattern_type=r.get("pattern_type", "glob"),
                priority=r.get("priority", 100),
                delete_input=r.get("delete_input", True),
            )
            for r in config.rules
        ],
    )


@router.patch("/config", response_model=ConfigResponse, tags=["Configuration"])
async def update_config(update: ConfigUpdate, persist: bool = False):
    """Update service configuration live.

    Args:
        update: Configuration update fields
        persist: Whether to save changes to disk (default False)
    """
    service = get_monitor_service()

    # Convert Pydantic update to dict
    update_dict = update.model_dump(exclude_unset=True)

    # Convert rules back to dicts if present
    if "rules" in update_dict:
        update_dict["rules"] = [r.model_dump() for r in update.rules]

    # Perform update
    service.update_config(update_dict, persist=persist)

    # Return new config
    return await get_config()


@router.post("/config/validate", tags=["Configuration"])
async def validate_config(update: ConfigUpdate):
    """Validate configuration without applying it."""
    # This is a bit complex as we'd need to mock the service
    # For now, we'll just check if the rules and basic fields are valid types
    # (Pydantic already did this via ConfigUpdate)
    return {"valid": True, "message": "Configuration is valid"}


@router.get("/profiles", response_model=list[ProfileResponse], tags=["Configuration"])
async def list_available_profiles():
    """List all available transcoding profiles."""
    from bulletproof.core.profile import BUILT_IN_PROFILES

    return [
        ProfileResponse(
            name=name,
            description=p.description,
            codec=p.codec,
            extension=p.extension,
            pixel_format=p.pixel_format,
            frame_rate=p.frame_rate,
            scale=p.scale,
            keyframe_interval=p.keyframe_interval,
        )
        for name, p in BUILT_IN_PROFILES.items()
    ]


@router.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str):
    """Get specific job details."""
    service = get_monitor_service()
    job = service.queue.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return JobResponse.from_queued_job(job)


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
        except Exception:
            # Client disconnected, can't send error
            pass
