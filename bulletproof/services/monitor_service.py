"""Monitor service - orchestrates folder monitoring and transcoding."""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from bulletproof.core.job import TranscodeJob
from bulletproof.core.monitor import FileInfo, FolderMonitor
from bulletproof.core.profile import BUILT_IN_PROFILES
from bulletproof.core.queue import QueuedJob, TranscodeQueue
from bulletproof.core.rules import PatternType, Rule, RuleEngine


class MonitorServiceError(Exception):
    """Base exception for MonitorService errors."""


class MonitorServiceConfig:
    """Configuration for MonitorService."""

    def __init__(
        self,
        watch_directory: Path,
        output_directory: Path,
        rules: "list[Rule | dict[str, Any]]",
        poll_interval: int = 5,
        delete_input: bool = True,
        persist_path: Path | None = None,
        log_level: str = "INFO",
        log_file: Path | None = None,
        api_host: str = "127.0.0.1",
        api_port: int = 8080,
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
            api_host: Host to bind for API server
            api_port: Port to bind for API server
        """
        self.watch_directory = Path(watch_directory)
        self.output_directory = Path(output_directory)
        self.rules = rules
        self.poll_interval = poll_interval
        self.delete_input = delete_input
        self.persist_path = Path(persist_path) if persist_path else None
        self.log_level = log_level
        self.log_file = Path(log_file) if log_file else None
        self.api_host = api_host
        self.api_port = api_port

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
    4. Manage background transcode task
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

        # Event system for real-time updates
        self.event_callback: Callable[[str, dict[str, Any]], None] | None = None

        # State tracking
        self._running = False
        self._paused = False
        self._stop_event = asyncio.Event()
        self._current_task: asyncio.Task | None = None
        self._start_time = datetime.now()
        self.logger.info(f"MonitorService initialized. watch_dir={config.watch_directory}")

    def emit_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit an event via callback.

        Args:
            event_type: Type of event (e.g., "job_update", "status")
            data: Event payload
        """
        if self.event_callback:
            try:
                self.event_callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Event callback failure: {e}")

    def _setup_logging(self) -> None:
        """Set up logging."""
        self.logger = logging.getLogger("bvp.monitor")
        self.logger.setLevel(getattr(logging, self.config.log_level))

        # Only add handlers if they don't exist
        if not self.logger.handlers:
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
        3. Manages transcode task
        """
        self._running = True
        self._start_time = datetime.now()
        self.logger.info(
            f"Service started. interval={self.config.poll_interval}s "
            f"watch_dir={self.config.watch_directory} "
            f"output_dir={self.config.output_directory}"
        )

        try:
            while not self._stop_event.is_set():
                try:
                    # Scan for new files
                    await self._scan_and_queue()

                    # Check if we need to start or manage a transcode task
                    await self._manage_transcode_task()

                    # Wait for next poll
                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(), timeout=self.config.poll_interval
                        )
                    except asyncio.TimeoutError:
                        # Normal timeout, continue loop
                        pass

                except Exception as e:
                    self.logger.error(f"Core service loop error: {e}", exc_info=True)
                    # Don't exit on error, keep trying
                    await asyncio.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Termination signal received (KeyboardInterrupt)")
        finally:
            self._running = False
            # Cleanup current task
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
                try:
                    await self._current_task
                except asyncio.CancelledError:
                    pass
            self.logger.info("Monitor service terminated")

    async def _scan_and_queue(self) -> None:
        """Scan directory and create transcode jobs for new files."""
        try:
            detected = self.monitor.scan()
            if detected:
                self.logger.debug(f"Scan detected {len(detected)} candidate file(s)")

            # Get stable files ready for processing
            stable_files = self.monitor.get_stable_files()
            for file_info in stable_files:
                self.emit_event("file_detected", {"filename": file_info.path.name})
                await self._create_job_for_file(file_info)

        except Exception as e:
            self.logger.error(f"Directory scan failed: {e}", exc_info=True)

    async def _create_job_for_file(self, file_info: FileInfo) -> None:
        """Create transcode job for a detected file.

        Args:
            file_info: FileInfo from monitor
        """
        try:
            # Match file to rule - pass filename string, not Path object
            rule = self.rule_engine.match(file_info.path.name)
            if not rule:
                self.logger.warning(f"No rule match found for: {file_info.path.name}")
                return

            # Get profile
            profile_name = rule.get("profile")
            if profile_name not in BUILT_IN_PROFILES:
                self.logger.error(f"Invalid profile name in rule: {profile_name}")
                return

            # Generate output path
            output_pattern = rule.get("output_pattern", "{filename}")
            output_file = self._generate_output_path(file_info.path, output_pattern, profile_name)

            # Create and queue job
            self.monitor.mark_processing(file_info)

            priority = rule.get("priority", 100)
            job = self.queue.add_from_file(file_info, output_file, profile_name, priority)

            self.emit_event(
                "job_queued",
                {
                    "job_id": job.id,
                    "input_file": str(job.input_file),
                    "output_file": str(job.output_file),
                    "profile": job.profile_name,
                    "priority": job.priority,
                },
            )

            self.logger.info(
                f"Job queued: id={job.id} input={file_info.path.name} "
                f"profile={profile_name} output={output_file.name} "
                f"priority={priority}"
            )

        except Exception as e:
            self.logger.error(f"Failed to create job for {file_info.path.name}: {e}", exc_info=True)
            self.monitor.mark_error(file_info)

    async def _manage_transcode_task(self) -> None:
        """Manage the background transcode task."""
        # If task is running, check if it's done or if we should pause
        if self._current_task:
            if self._current_task.done():
                # Task finished, clean up
                try:
                    await self._current_task
                except Exception as e:
                    self.logger.error(f"Worker task exception: {e}")
                self._current_task = None
            return

        # No task running, check if we should start one
        if not self._paused:
            job = self.queue.get_pending()
            if job:
                self._current_task = asyncio.create_task(self._execute_job(job))

    async def _execute_job(self, job: Any) -> None:
        """Worker function for executing a single job.

        Args:
            job: QueuedJob to execute
        """
        try:
            # Mark as processing
            job = self.queue.get_next()
            if not job:
                return

            self.logger.info(
                f"Worker started: id={job.id} "
                f"input={job.input_file.name} profile={job.profile_name}"
            )

            self.emit_event(
                "job_started",
                {
                    "job_id": job.id,
                    "input_file": str(job.input_file),
                    "profile": job.profile_name,
                },
            )

            # Execute transcode
            profile = BUILT_IN_PROFILES[job.profile_name]
            transcode_job = TranscodeJob(
                input_file=job.input_file,
                output_file=job.output_file,
                profile=profile,
            )

            # Define progress callback to update queued job status
            last_p = -1.0

            def update_progress(p: float):
                nonlocal last_p
                job.progress = p
                # Throttle updates: only emit if progress increased by > 0.5%
                if p - last_p >= 0.5 or p >= 100.0:
                    self.emit_event(
                        "job_progress",
                        {
                            "job_id": job.id,
                            "progress": round(p, 1),
                        },
                    )
                    last_p = p

            # Execute asynchronously
            success = await transcode_job.execute(progress_callback=update_progress)

            if success:
                self.queue.mark_complete(job)
                self.emit_event(
                    "job_complete",
                    {
                        "job_id": job.id,
                        "output_file": str(job.output_file),
                    },
                )
                self.logger.info(f"Worker completed: id={job.id} output={job.output_file.name}")

                # Delete input if configured
                if self.config.delete_input and job.input_file.exists():
                    try:
                        job.input_file.unlink()
                        self.logger.debug(f"File deleted: {job.input_file.name}")
                    except Exception as e:
                        self.logger.warning(f"File deletion failed: {job.input_file.name}: {e}")
            else:
                error_msg = transcode_job.error_message or "Unknown error"
                self.queue.mark_error(job, error_msg)
                self.emit_event(
                    "job_error",
                    {
                        "job_id": job.id,
                        "error": error_msg,
                    },
                )
                self.logger.error(
                    f"Worker failed: id={job.id} input={job.input_file.name} error={error_msg}"
                )

        except asyncio.CancelledError:
            self.logger.info(f"Worker cancelled: id={job.id} input={job.input_file.name}")
            if job:
                self.queue.mark_cancelled(job)
                self.emit_event("job_cancelled", {"job_id": job.id})
            raise
        except Exception as e:
            error_msg = str(e)
            if job:
                self.queue.mark_error(job, error_msg)
                self.emit_event(
                    "job_error",
                    {
                        "job_id": job.id,
                        "error": error_msg,
                    },
                )
            self.logger.error(f"Worker execution exception: id={job.id} error={e}", exc_info=True)

    def pause(self) -> None:
        """Pause processing queue."""
        self._paused = True
        self.emit_event("status_changed", {"paused": True})
        self.logger.info("Service PAUSED: Job processing suspended")

    def resume(self) -> None:
        """Resume processing queue."""
        self._paused = False
        self.emit_event("status_changed", {"paused": False})
        self.logger.info("Service RESUMED: Job processing restored")

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.

        Args:
            job_id: ID of job to cancel

        Returns:
            True if cancelled, False otherwise
        """
        job = self.queue.get_job(job_id)
        if not job:
            return False

        # If it's the current task, cancel the task
        current_job = self.queue.get_current()
        if current_job and current_job.id == job_id and self._current_task:
            self._current_task.cancel()
            return True

        if job.status == "pending":
            self.queue.mark_cancelled(job)
            self.logger.info(f"Job cancelled (pending): id={job_id}")
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
        self.logger.info(f"Job retry initiated: original_id={job_id} new_id={new_job.id}")
        return True

    def clear_queue(self) -> None:
        """Clear all pending jobs from queue."""
        self.queue.clear()
        self.logger.info("Queue cleared: All pending jobs removed")

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
        self.logger.info("Graceful stop requested")
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

    def get_history(self, limit: int = 10) -> list[QueuedJob]:
        """Get recent processing history.

        Args:
            limit: Number of recent jobs to return

        Returns:
            List of QueuedJob objects
        """
        return self.queue.get_history(limit)

    def update_config(self, updates: dict[str, Any], persist: bool = False) -> None:
        """Update service configuration live.

        Args:
            updates: Dict of config updates (rules, poll_interval, etc.)
            persist: Whether to save changes to the original config file
        """
        if "rules" in updates:
            # Convert dicts to Rule objects for MonitorConfig
            new_rules = []
            for r in updates["rules"]:
                if isinstance(r, dict):
                    new_rules.append(
                        Rule(
                            pattern=r["pattern"],
                            profile=r["profile"],
                            output_pattern=r.get("output_pattern", "{filename}"),
                            pattern_type=PatternType(r.get("pattern_type", "glob")),
                            delete_input=r.get("delete_input", True),
                            priority=r.get("priority", 100),
                        )
                    )
                else:
                    new_rules.append(r)

            # Update RuleEngine and Config
            self.rule_engine = RuleEngine(new_rules)
            self.config.rules = new_rules
            self.logger.info(f"Configuration updated: rules_count={len(new_rules)}")

        if "poll_interval" in updates:
            self.config.poll_interval = int(updates["poll_interval"])
            self.logger.info(f"Configuration updated: poll_interval={self.config.poll_interval}s")

        if "delete_input" in updates:
            self.config.delete_input = bool(updates["delete_input"])
            self.logger.info(f"Configuration updated: delete_input={self.config.delete_input}")

        if "log_level" in updates:
            level = updates["log_level"].upper()
            self.config.log_level = level
            # Update logger and all handlers
            self.logger.setLevel(getattr(logging, level))
            for handler in self.logger.handlers:
                handler.setLevel(getattr(logging, level))
            self.logger.info(f"Configuration updated: log_level={level}")

        # Persist to disk if requested (simplified - just log for now)
        if persist:
            self.logger.info("Configuration updated in memory (disk persistence not implemented)")
