"""FastAPI server for bulletproof video playback dashboard."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from bulletproof.api.routes import router, set_monitor_service
from bulletproof.services.monitor_service import MonitorService

logger = logging.getLogger(__name__)

# Global service instance
_service: Optional[MonitorService] = None
_service_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    global _service, _service_task

    # Startup
    logger.info("Starting bulletproof dashboard API...")

    # Service will be set externally via set_service()
    # or can be initialized here if config is available

    yield

    # Shutdown
    logger.info("Shutting down bulletproof dashboard API...")
    if _service:
        _service.stop()
    if _service_task:
        _service_task.cancel()
        try:
            await _service_task
        except asyncio.CancelledError:
            pass


def create_app(
    monitor_service: Optional[MonitorService] = None,
    enable_cors: bool = True,
    static_dir: Optional[Path] = None,
) -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        monitor_service: Optional MonitorService instance to use
        enable_cors: Enable CORS middleware for development
        static_dir: Directory for static files (dashboard UI)

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Bulletproof Video Playback Dashboard",
        description="Monitor and control video transcoding workflows",
        version="3.1.0",
        lifespan=lifespan,
    )

    # CORS middleware for development
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include API routes
    app.include_router(router, prefix="/api/v1")

    # Mount static files if provided
    if static_dir and static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    # Set monitor service if provided
    if monitor_service:
        set_service(app, monitor_service)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Bulletproof Video Playback Dashboard",
            "version": "3.1.0",
            "api": "/api/v1",
            "docs": "/docs",
            "timestamp": datetime.now().isoformat(),
        }

    return app


def set_service(app: FastAPI, service: MonitorService):
    """Set the monitor service for the application.

    Args:
        app: FastAPI application
        service: MonitorService instance
    """
    global _service
    _service = service
    _service._start_time = datetime.now()
    set_monitor_service(service)
    logger.info("MonitorService attached to API")


def start_service_background(service: MonitorService):
    """Start the monitor service in the background.

    Args:
        service: MonitorService to run
    """
    global _service_task

    async def run_service():
        try:
            await service.run()
        except Exception as e:
            logger.error(f"Error running monitor service: {e}", exc_info=True)

    _service_task = asyncio.create_task(run_service())
    logger.info("MonitorService started in background")


if __name__ == "__main__":
    # For development/testing
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )
