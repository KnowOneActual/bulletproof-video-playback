"""Main monitoring service that orchestrates folder watching and transcoding."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from bulletproof.core.monitor import FolderMonitor, FileInfo
from bulletproof.core.queue import TranscodeQueue, QueuedJob, JobStatus
from bulletproof.core.rules import RuleEngine
from bulletproof.core.config import MonitorConfig
from bulletproof.core.job import TranscodeJob
from bulletproof.core import get_profile


class MonitorLogger:
    """Structured logging for monitoring service."""

    def __init__(self, name: str, log_file: Optional[Path] = None, level: str = "INFO"):
        """Initialize logger.
        
        Args:
            name: Logger name
            log_file: Optional file to log to
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def file_detected(self, file_info: FileInfo) -> None:
        """Log file detection."""
        size_mb = file_info.size / (1024 * 1024)
        self.logger.info(f"📁 Detected: {file_info.path.name} ({size_mb:.1f} MB)")

    def file_stable(self, file_info: FileInfo, profile: str) -> None:
        """Log file stability and profile match."""
        self.logger.info(f"✓ Stable: {file_info.path.name} → {profile}")

    def job_queued(self, job: QueuedJob) -> None:
        """Log job queuing."""
        self.logger.info(
            f"📋 Queued: {job.input_file.name} ({job.profile_name})"
        )

    def job_started(self, job: QueuedJob) -> None:
        """Log job start."""
        self.logger.info(f"▶️  Started: {job.input_file.name}")

    def job_complete(self, job: QueuedJob, duration: float) -> None:
        """Log successful job completion."""
        minutes = duration / 60
        self.logger.info(
            f"✅ Complete: {job.input_file.name} ({minutes:.1f}m)"
        )

    def job_error(self, job: QueuedJob, error: str) -> None:
        """Log job error."""
        self.logger.error(
            f"❌ Error: {job.input_file.name} - {error}"
        )

    def status(self, pending: int, processing: int, completed: int) -> None:
        """Log status."""
        self.logger.info(
            f"📊 Status: {pending} pending, {processing} processing, {completed} completed"
        )


class MonitorService:
    """Main monitoring service.
    
    Orchestrates:
    - FolderMonitor (watches directory)
    - RuleEngine (matches files to profiles)
    - TranscodeQueue (manages jobs)
    - TranscodeJob execution (performs encoding)
    """

    def __init__(self, config: MonitorConfig):
        """Initialize monitor service.
        
        Args:
            config: MonitorConfig instance
        """
        self.config = config

        # Initialize components
        self.monitor = FolderMonitor(config.watch_directory)
        self.rules = RuleEngine(config.rules)
        self.queue = TranscodeQueue(config.persist_path)

        # Initialize logger
        self.logger = MonitorLogger(
            "bulletproof.monitor",
            config.log_file,
            config.log_level,
        )

        # State
        self._running = False
        self._current_job: Optional[QueuedJob] = None

    async def run(self) -> None:
        """Main service loop.
        
        Continuously:
        1. Scan directory for new files
        2. Match files to rules
        3. Queue jobs
        4. Process jobs sequentially
        """
        self._running = True
        self.logger.logger.info("🚀 Monitor service starting...")
        self.logger.logger.info(f"   Watch: {self.config.watch_directory}")
        self.logger.logger.info(f"   Output: {self.config.output_directory}")
        self.logger.logger.info(f"   Poll: every {self.config.poll_interval}s")

        try:
            while self._running:
                # Scan for new files
                detected = self.monitor.scan()
                if detected:
                    self.logger.logger.debug(f"Scanned {len(detected)} new files")

                # Get stable files and queue them
                stable_files = self.monitor.get_stable_files()
                for file_info in stable_files:
                    # Match to profile
                    profile = self.rules.find_profile(file_info.path.name)
                    if not profile:
                        self.logger.logger.warning(
                            f"⚠️  No matching rule for: {file_info.path.name}"
                        )
                        self.monitor.mark_processed(file_info)
                        continue

                    # Get output path
                    output_path = self.rules.get_output_path(
                        file_info.path,
                        self.config.output_directory,
                    )
                    if not output_path:
                        self.logger.logger.error(
                            f"❌ Could not determine output path for: {file_info.path.name}"
                        )
                        self.monitor.mark_error(file_info)
                        continue

                    # Create job
                    job = self.queue.add_from_file(
                        file_info,
                        output_path,
                        profile,
                    )
                    self.monitor.mark_processing(file_info)
                    self.logger.file_stable(file_info, profile)
                    self.logger.job_queued(job)

                # Process next queued job
                next_job = self.queue.get_next()
                if next_job:
                    await self._process_job(next_job)

                # Log status
                status = self.queue.get_status()
                if status["total_queued"] > 0 or status["pending"] > 0:
                    self.logger.status(
                        status["pending"],
                        status["processing"],
                        status["completed"],
                    )

                # Wait before next poll
                await asyncio.sleep(self.config.poll_interval)

        except KeyboardInterrupt:
            self.logger.logger.info("⏸️  Received interrupt signal")
        except Exception as e:
            self.logger.logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self._running = False
            self.logger.logger.info("🛑 Monitor service stopped")

    async def _process_job(self, job: QueuedJob) -> None:
        """Process a single transcode job.
        
        Args:
            job: QueuedJob to process
        """
        self._current_job = job
        start_time = datetime.now()
        self.logger.job_started(job)

        try:
            # Verify profile exists
            try:
                profile = get_profile(job.profile_name)
            except KeyError:
                raise ValueError(f"Profile not found: {job.profile_name}")

            # Create transcode job
            transcode_job = TranscodeJob(
                input_file=job.input_file,
                output_file=job.output_file,
                profile=profile,
                speed_preset="normal",
            )

            # Execute transcode
            async for progress in transcode_job.execute_async():
                # Log progress periodically
                if int(progress.percent) % 25 == 0 and progress.percent > 0:
                    self.logger.logger.debug(
                        f"  {progress.percent:.1f}% - {progress.fps:.1f} fps"
                    )

            # Check for errors
            if transcode_job.status == "error":
                raise Exception(transcode_job.error_message or "Unknown error")

            # Mark complete
            duration = (datetime.now() - start_time).total_seconds()
            self.queue.mark_complete(job)
            self.logger.job_complete(job, duration)

            # Delete input if configured
            if self.config.delete_input:
                try:
                    job.input_file.unlink()
                    self.logger.logger.debug(
                        f"Deleted input: {job.input_file.name}"
                    )
                except Exception as e:
                    self.logger.logger.warning(
                        f"Could not delete input {job.input_file.name}: {e}"
                    )

        except Exception as e:
            error_msg = str(e)[:200]
            self.queue.mark_error(job, error_msg)
            self.logger.job_error(job, error_msg)

        finally:
            self._current_job = None

    def get_status(self) -> dict:
        """Get current service status.
        
        Returns:
            Dict with status information
        """
        queue_status = self.queue.get_status()
        return {
            "running": self._running,
            "watch_directory": str(self.config.watch_directory),
            "output_directory": str(self.config.output_directory),
            "current_job": str(self._current_job.input_file.name)
            if self._current_job
            else None,
            "queue": queue_status,
            "rules": len(self.config.rules),
        }

    def stop(self) -> None:
        """Stop the service."""
        self._running = False
