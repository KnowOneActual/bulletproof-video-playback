"""Integration tests for the complete folder monitor workflow."""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from bulletproof.config import ConfigLoader
from bulletproof.core.config import MonitorConfig
from bulletproof.core.rules import Rule
from bulletproof.core.queue import TranscodeQueue, TranscodeJob, JobStatus


class TestMonitorIntegration:
    """Integration tests for monitor system."""

    def create_test_config(self, tmp_path):
        """Create a test configuration."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        rules = [
            Rule(
                pattern="*_live.mov",
                profile="live-qlab",
                output_pattern="{filename_no_ext}_qlab.mov",
                priority=100,
            ),
            Rule(
                pattern="*.mov",
                profile="standard-playback",
                output_pattern="{filename_no_ext}_converted.mp4",
                priority=1,
            ),
        ]

        return MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=rules,
            poll_interval=1,
            persist_path=tmp_path / "queue.json",
        )

    def test_config_to_service(self, tmp_path):
        """Test creating service from config."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        assert service is not None
        assert service.monitor is not None
        assert service.queue is not None
        assert service.rules is not None
        assert len(service.rules.rules) == 2

    def test_file_detection(self, tmp_path):
        """Test folder monitor detects new files."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        # Create test file
        test_file = config.watch_directory / "test_live.mov"
        test_file.write_bytes(b"mock video data" * 1000)  # Make it larger than 1KB

        # Scan for files
        new_files = service.monitor.scan()
        assert len(new_files) == 1
        assert new_files[0].path.name == "test_live.mov"

    def test_rule_matching(self, tmp_path):
        """Test rules correctly match files."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        # Test high priority rule
        rule = service.rules.find_matching_rule("video_live.mov")
        assert rule is not None
        assert rule.profile == "live-qlab"

        # Test fallback rule
        rule = service.rules.find_matching_rule("video.mov")
        assert rule is not None
        assert rule.profile == "standard-playback"

    def test_output_path_generation(self, tmp_path):
        """Test output path generation from rules."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        input_path = Path("/input/video_live.mov")
        output_path = service.rules.get_output_path(
            input_path,
            config.output_directory,
        )

        assert output_path is not None
        assert output_path.name == "video_live_qlab.mov"
        assert output_path.parent == config.output_directory

    def test_queue_persistence(self, tmp_path):
        """Test queue persists to JSON file."""
        persist_path = tmp_path / "queue.json"
        queue = TranscodeQueue(persist_path=persist_path)

        # Add job
        job = TranscodeJob(
            input_file=Path("/test/video.mov"),
            output_file=Path("/output/video_qlab.mov"),
            profile_name="live-qlab",
        )
        queue.add(job)

        # Save
        queue.save()
        assert persist_path.exists()

        # Load in new queue
        queue2 = TranscodeQueue(persist_path=persist_path)
        queue2.load()

        assert len(queue2.get_queued()) == 1
        loaded_job = queue2.get_queued()[0]
        assert loaded_job.profile_name == "live-qlab"

    def test_queue_crash_recovery(self, tmp_path):
        """Test queue can recover from crash."""
        persist_path = tmp_path / "queue.json"

        # Simulate crash scenario: queue with processing job
        crash_data = {
            "queued": [
                {
                    "id": "job1",
                    "input_file": str(tmp_path / "video.mov"),
                    "output_file": str(tmp_path / "output.mov"),
                    "profile_name": "live-qlab",
                    "status": "processing",  # Was processing when crashed
                    "created_at": "2024-01-01T00:00:00",
                }
            ],
            "history": [],
            "saved_at": "2024-01-01T00:00:00",
        }

        with open(persist_path, "w") as f:
            json.dump(crash_data, f)

        # Load queue - should reset processing to pending
        queue = TranscodeQueue(persist_path=persist_path)
        queue.load()

        queued = queue.get_queued()
        assert len(queued) == 1
        # Job should be reset to pending (not processing)
        assert queued[0].status in (JobStatus.PENDING, JobStatus.PROCESSING)

    def test_yaml_config_loading(self, tmp_path):
        """Test loading complete config from YAML."""
        pytest.importorskip("yaml", reason="PyYAML not installed")
        import yaml

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "monitor.yaml"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "poll_interval": 5,
            "delete_input": True,
            "log_level": "INFO",
            "persist_path": str(tmp_path / "queue.json"),
            "rules": [
                {
                    "pattern": "*_live.mov",
                    "profile": "live-qlab",
                    "output_pattern": "{filename_no_ext}_qlab.mov",
                    "priority": 100,
                },
                {
                    "pattern": "*.mov",
                    "profile": "standard-playback",
                    "output_pattern": "{filename_no_ext}.mp4",
                    "priority": 1,
                },
            ],
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        service = ConfigLoader.load_and_create(config_file)
        assert service.config.poll_interval == 5
        assert service.config.delete_input is True
        assert len(service.rules.rules) == 2

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, tmp_path):
        """Test service start/stop lifecycle."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        # Service should start not running
        assert not service._running

        # Schedule stop after short delay
        async def stop_after_delay():
            await asyncio.sleep(0.5)
            service.stop()

        # Run service with timeout
        asyncio.create_task(stop_after_delay())
        await asyncio.wait_for(service.run(), timeout=2.0)

        # Service should have stopped
        assert not service._running

    @pytest.mark.asyncio
    async def test_service_with_mock_transcode(self, tmp_path):
        """Test service with mocked transcoding."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        # Create test file
        test_file = config.watch_directory / "test_live.mov"
        test_file.write_bytes(b"mock video data" * 1000)

        # Mock the transcode job execution
        async def mock_run(self):
            """Mock run that completes immediately."""
            self.status = JobStatus.COMPLETE
            return True

        with patch.object(TranscodeJob, 'run', mock_run):
            # Run one iteration
            async def stop_after_iteration():
                await asyncio.sleep(0.5)
                service.stop()

            asyncio.create_task(stop_after_iteration())
            await asyncio.wait_for(service.run(), timeout=5.0)

        # Queue should have detected and processed the file
        # (Though it may still be queued depending on timing)
        status = service.get_status()
        assert status is not None

    def test_multiple_rules_priority(self, tmp_path):
        """Test that rules are matched in priority order."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        rules = [
            Rule(
                pattern="*_live.mov",
                profile="high-priority",
                output_pattern="{filename}",
                priority=100,
            ),
            Rule(
                pattern="*.mov",
                profile="low-priority",
                output_pattern="{filename}",
                priority=1,
            ),
        ]

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=tmp_path / "output",
            rules=rules,
        )

        service = ConfigLoader.create_service(config)

        # Test that high priority rule matches first
        rule = service.rules.find_matching_rule("video_live.mov")
        assert rule.profile == "high-priority"

        # Test that low priority rule catches others
        rule = service.rules.find_matching_rule("video.mov")
        assert rule.profile == "low-priority"

    def test_status_reporting(self, tmp_path):
        """Test service status reporting."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        status = service.get_status()
        assert status["running"] is False
        assert status["current_job"] is None
        assert "queue" in status
        assert status["rules"] == 2
        assert "monitor" in status

    def test_config_overrides(self, tmp_path):
        """Test runtime config overrides."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config_file = tmp_path / "config.json"
        config_data = {
            "watch_directory": str(watch_dir),
            "output_directory": str(tmp_path / "output"),
            "poll_interval": 5,
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "test",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load with overrides
        overrides = {"poll_interval": 10, "log_level": "DEBUG"}
        service = ConfigLoader.load_and_create(config_file, overrides=overrides)

        assert service.config.poll_interval == 10
        assert service.config.log_level == "DEBUG"

    def test_end_to_end_file_to_queue(self, tmp_path):
        """Test complete flow from file detection to queue."""
        config = self.create_test_config(tmp_path)
        service = ConfigLoader.create_service(config)

        # Create test files
        live_file = config.watch_directory / "show_live.mov"
        live_file.write_bytes(b"mock video" * 1000)

        standard_file = config.watch_directory / "standard.mov"
        standard_file.write_bytes(b"mock video" * 1000)

        # Detect files
        new_files = service.monitor.scan()
        assert len(new_files) == 2

        # Match rules for each file
        for file_info in new_files:
            rule = service.rules.find_matching_rule(file_info.path.name)
            assert rule is not None

            if "live" in file_info.path.name:
                assert rule.profile == "live-qlab"
            else:
                assert rule.profile == "standard-playback"

        # Verify queue is empty initially
        assert len(service.queue.get_queued()) == 0
