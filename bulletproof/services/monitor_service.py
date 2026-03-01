"""Monitor service - orchestrates folder monitoring and transcoding."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from bulletproof.core.job import TranscodeJob
from bulletproof.core.monitor import FileInfo, FolderMonitor
from bulletproof.core.profile import BUILT_IN_PROFILES
from bulletproof.core.queue import TranscodeQueue
from bulletproof.core.rules import RuleEngine


class MonitorServiceError(Exception):
    """Base exception for MonitorService errors."""


class MonitorServiceConfig:
    """Configuration for MonitorService."""

    def __init__(
        self,
        watch_directory: Path,
        output_directory: Path,
        rules: list[dict[str, Any]],
        poll_interval: int = 5,
        delete_input: bool = True,
        persist_path: Optional[Path] = None,
        log_level: str = "INFO",
        log_file: Optional[Path] = None,
    ):
        """Initialize service configuration.

        Args:
            watch_directory: Directory to monitor for videos
            output_directory: Directory for transcoded output
            rules: List of rule dictionaries for RuleEngine
            poll_interval: Seconds between folder scans
            delete_input: Whether to delete input files after successful transcode
            persist_path: Path to persist queue state (JSON)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional file path for logging output
        """
        self.watch_directory = Path(watch_directory)
        self.output_directory = Path(output_directory)
        self.rules = rules
        self.poll_interval = poll_interval
        self.delete_input = delete_input
        self.persist_path = Path(persist_path) if persist_path else None
        self.log_level = log_level
        self.log_file = Path(log_file) if log_file else None

        # Validate
        if not self.watch_directory.exists():
            raise MonitorServiceError(f"Watch directory does not exist: {self.watch_directory}")
        if not self.watch_directory.is_dir():
            raise MonitorServiceError(f"Watch path is not a directory: {self.watch_directory}")

        # Create output directory if needed
        self.output_directory.mkdir(parents=True, exist_ok=True)


class MonitorService:
    """Orchestrates folder monitoring and video transcoding.

    Main workflow:
    1. Scan watch directory for video files
    2. Match detected files to rules
    3. Create transcode jobs in queue
    4. Process queue sequentially
    5. Update file status
    6. Persist state and handle errors
    """

    def __init__(self, config: MonitorServiceConfig):
        """Initialize monitor service.

        Args:
            config: MonitorServiceConfig with service settings
        """
        self.config = config
        self._setup_logging()

        # Initialize components
        self.monitor = FolderMonitor(config.watch_directory)
        self.queue = TranscodeQueue(config.persist_path)
        self.rule_engine = RuleEngine(config.rules)

        # State tracking
        self._running = False
        self._paused = False
        self._stop_event = asyncio.Event()
        self.logger.info(f"MonitorService initialized for {config.watch_directory}")

    def _setup_logging(self) -> None:
        """Set up logging."""
        self.logger = logging.getLogger("bvp.monitor")
        self.logger.setLevel(getattr(logging, self.config.log_level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.log_level))
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if self.config.log_file:
            self.config.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(getattr(logging, self.config.log_level))
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    async def run(self) -> None:
        """Main service loop - runs until stop() is called.

        Continuously:
        1. Scans for new files
        2. Matches files to rules
        3. Processes transcode queue
        """
        self._running = True
        self.logger.info(f"Starting monitor service (poll interval: {self.config.poll_interval}s)")

        try:
            while not self._stop_event.is_set():
                try:
                    # Scan for new files
                    await self._scan_and_queue()

                    # Process queue
                    await self._process_queue()

                    # Wait for next poll
                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(), timeout=self.config.poll_interval
                        )
                    except asyncio.TimeoutError:
                        # Normal timeout, continue loop
                        pass

                except Exception as e:
                    self.logger.error(f"Error in monitor loop: {e}", exc_info=True)
                    # Don't exit on error, keep trying
                    await asyncio.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt received")
        finally:
            self._running = False
            self.logger.info("Monitor service stopped")

    async def _scan_and_queue(self) -> None:
        """Scan directory and create transcode jobs for new files."""
        try:
            detected = self.monitor.scan()
            if detected:
                self.logger.debug(f"Detected {len(detected)} new file(s)")

            # Get stable files ready for processing
            stable_files = self.monitor.get_stable_files()
            for file_info in stable_files:
                await self._create_job_for_file(file_info)

        except Exception as e:
            self.logger.error(f"Error scanning directory: {e}", exc_info=True)

    async def _create_job_for_file(self, file_info: FileInfo) -> None:
        """Create transcode job for a detected file.

        Args:
            file_info: FileInfo from monitor
        """
        try:
            # Match file to rule - pass filename string, not Path object
            rule = self.rule_engine.match(file_info.path.name)
            if not rule:
                self.logger.warning(f"No rule matched for {file_info.path.name}")
                return

            # Get profile
            profile_name = rule.get("profile")
            if profile_name not in BUILT_IN_PROFILES:
                self.logger.error(f"Profile not found: {profile_name}")
                return

            # Generate output path
            output_pattern = rule.get("output_pattern", "{filename}")
            output_file = self._generate_output_path(file_info.path, output_pattern, profile_name)

            # Create and queue job
            self.monitor.mark_processing(file_info)

            # Fix: Actually add to queue!
            priority = rule.get("priority", 100)
            job = self.queue.add_from_file(file_info, output_file, profile_name, priority)

            self.logger.info(
                f"Queued: {file_info.path.name} → {profile_name} "
                f"→ {output_file.name} (ID: {job.id})"
            )

        except Exception as e:
            self.logger.error(f"Error creating job for {file_info.path.name}: {e}", exc_info=True)
            self.monitor.mark_error(file_info)

    async def _process_queue(self) -> None:
        """Process next job in queue."""
        # Don't process if paused
        if self._paused:
            return

        job = self.queue.get_pending()
        if not job:
            return

        try:
            # Mark as processing
            job = self.queue.get_next()
            if not job:
                return

            self.logger.info(f"Processing: {job.input_file.name} ({job.profile_name})")

            # Execute transcode
            profile = BUILT_IN_PROFILES[job.profile_name]
            transcode_job = TranscodeJob(
                input_file=job.input_file,
                output_file=job.output_file,
                profile=profile,
            )

            # Non-blocking execution (to allow progress updates later)
            # For now keeping it simple as per original design
            success = transcode_job.execute()

            if success:
                self.queue.mark_complete(job)
                self.logger.info(f"Completed: {job.output_file.name}")

                # Delete input if configured
                if self.config.delete_input and job.input_file.exists():
                    try:
                        job.input_file.unlink()
                        self.logger.debug(f"Deleted input: {job.input_file.name}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete {job.input_file.name}: {e}")
            else:
                error_msg = transcode_job.error_message or "Unknown error"
                self.queue.mark_error(job, error_msg)
                self.logger.error(f"Failed: {job.input_file.name} - {error_msg}")

        except Exception as e:
            error_msg = str(e)
            if job:
                self.queue.mark_error(job, error_msg)
            self.logger.error(f"Exception processing queue job: {e}", exc_info=True)

    def pause(self) -> None:
        """Pause processing queue."""
        self._paused = True
        self.logger.info("Service PAUSED (queue processing stopped)")

    def resume(self) -> None:
        """Resume processing queue."""
        self._paused = False
        self.logger.info("Service RESUMED (queue processing started)")

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job.

        Args:
            job_id: ID of job to cancel

        Returns:
            True if cancelled, False otherwise
        """
        job = self.queue.get_job(job_id)
        if not job:
            return False

        if job.status == "pending":
            self.queue.mark_cancelled(job)
            self.logger.info(f"Cancelled job: {job_id}")
            return True
        return False

    def retry_job(self, job_id: str) -> bool:
        """Retry a failed or completed job.

        Args:
            job_id: ID of job to retry

        Returns:
            True if retried, False otherwise
        """
        old_job = self.queue.get_job(job_id)
        if not old_job:
            return False

        # Create new job from old one
        from bulletproof.core.queue import QueuedJob

        new_job = QueuedJob(
            input_file=old_job.input_file,
            output_file=old_job.output_file,
            profile_name=old_job.profile_name,
            priority=old_job.priority,
        )

        self.queue.add(new_job)
        self.logger.info(f"Retrying job {job_id} as {new_job.id}")
        return True

    def clear_queue(self) -> None:
        """Clear all pending jobs from queue."""
        self.queue.clear()
        self.logger.info("Queue cleared")

    def _generate_output_path(self, input_file: Path, pattern: str, profile_name: str) -> Path:
        """Generate output file path from template.

        Args:
            input_file: Input file path
            pattern: Output pattern template
            profile_name: Profile name

        Returns:
            Generated output Path
        """
        filename = input_file.name
        filename_no_ext = input_file.stem

        # Replace variables in pattern
        output_name = (
            pattern.replace("{filename}", filename)
            .replace("{filename_no_ext}", filename_no_ext)
            .replace("{profile}", profile_name)
        )

        return self.config.output_directory / output_name

    def stop(self) -> None:
        """Request service to stop gracefully."""
        self.logger.info("Stop requested")
        self._stop_event.set()

    def get_status(self) -> dict[str, Any]:
        """Get current service status.

        Returns:
            Dict with monitoring status information
        """
        return {
            "running": self._running,
            "paused": self._paused,
            "watch_directory": str(self.config.watch_directory),
            "output_directory": str(self.config.output_directory),
            "poll_interval": self.config.poll_interval,
            "timestamp": datetime.now().isoformat(),
            "monitor": self.monitor.get_status(),
            "queue": self.queue.get_status(),
        }

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent processing history.

        Args:
            limit: Number of recent jobs to return

        Returns:
            List of job dicts
        """
        jobs = self.queue.get_history(limit)
        return [job.to_dict() for job in jobs]
