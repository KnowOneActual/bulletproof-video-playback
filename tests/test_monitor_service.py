"""Tests for MonitorService orchestration."""

import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch, AsyncMock

import pytest

from bulletproof.core.config import MonitorConfig
from bulletproof.core.monitor import FileInfo, FolderMonitor
from bulletproof.core.rules import Rule, PatternType
from bulletproof.services.monitor_service import MonitorService, MonitorLogger


class TestMonitorLogger:
    """Test MonitorLogger."""

    def test_logger_creation(self):
        """Test logger can be created."""
        logger = MonitorLogger("test", level="DEBUG")
        assert logger.logger.name == "test"
        assert logger.logger.level == 10  # DEBUG

    def test_logger_with_file(self, tmp_path):
        """Test logger with file output."""
        log_file = tmp_path / "test.log"
        logger = MonitorLogger("test", log_file=log_file)
        logger.logger.info("Test message")
        assert log_file.exists()

    def test_logger_methods(self, caplog):
        """Test logger methods."""
        logger = MonitorLogger("test")
        file_info = FileInfo(
            path=Path("/test/video.mov"),
            size=1024 * 1024,
            modified=0,
        )
        logger.file_detected(file_info)
        assert "Detected" in caplog.text


class TestMonitorConfig:
    """Test MonitorConfig."""

    def test_config_validation(self, tmp_path):
        """Test config validates watch directory."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            MonitorConfig(
                watch_directory=nonexistent,
                output_directory=tmp_path,
            )

    def test_config_creates_output_dir(self, tmp_path):
        """Test config creates output directory if missing."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
        )

        assert output_dir.exists()

    def test_config_to_dict(self, tmp_path):
        """Test config to_dict method."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        rule = Rule(
            pattern="*.mov",
            profile="test-profile",
            output_pattern="{filename}",
        )

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[rule],
            poll_interval=10,
        )

        data = config.to_dict()
        assert data["poll_interval"] == 10
        assert len(data["rules"]) == 1

    @pytest.mark.skipif(
        not pytest.importorskip("yaml", minversion=None),
        reason="PyYAML not installed",
    )
    def test_config_from_yaml(self, tmp_path):
        """Test loading config from YAML."""
        import yaml

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        yaml_file = tmp_path / "config.yaml"
        yaml_data = {
            "watch_directory": str(watch_dir),
            "output_directory": "output",
            "poll_interval": 10,
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "test",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(yaml_file, "w") as f:
            yaml.dump(yaml_data, f)

        config = MonitorConfig.from_yaml(yaml_file)
        assert config.poll_interval == 10
        assert len(config.rules) == 1
        assert config.rules[0].profile == "test"

    def test_config_from_json(self, tmp_path):
        """Test loading config from JSON."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        json_file = tmp_path / "config.json"
        json_data = {
            "watch_directory": str(watch_dir),
            "output_directory": "output",
            "poll_interval": 10,
            "rules": [
                {
                    "pattern": "*.mov",
                    "profile": "test",
                    "output_pattern": "{filename}",
                }
            ],
        }

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        config = MonitorConfig.from_json(json_file)
        assert config.poll_interval == 10
        assert len(config.rules) == 1

    def test_config_save_json(self, tmp_path):
        """Test saving config to JSON."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=tmp_path / "output",
            poll_interval=15,
        )

        json_file = tmp_path / "saved.json"
        config.save_json(json_file)
        assert json_file.exists()

        # Reload and verify
        loaded = MonitorConfig.from_json(json_file)
        assert loaded.poll_interval == 15


class TestMonitorService:
    """Test MonitorService."""

    def _create_service(self, tmp_path):
        """Create a test MonitorService."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        rule = Rule(
            pattern="*.mov",
            profile="live-qlab",
            output_pattern="{filename_no_ext}_qlab.mov",
        )

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[rule],
            poll_interval=1,
        )

        return MonitorService(config)

    def test_service_creation(self, tmp_path):
        """Test MonitorService can be created."""
        service = self._create_service(tmp_path)
        assert service.monitor is not None
        assert service.rules is not None
        assert service.queue is not None
        assert service.logger is not None

    def test_service_status(self, tmp_path):
        """Test service status reporting."""
        service = self._create_service(tmp_path)
        status = service.get_status()
        assert status["running"] is False
        assert status["current_job"] is None
        assert "queue" in status
        assert status["rules"] == 1

    def test_service_stop(self, tmp_path):
        """Test service stop."""
        service = self._create_service(tmp_path)
        service._running = True
        service.stop()
        assert service._running is False

    @pytest.mark.asyncio
    async def test_service_run_empty_directory(self, tmp_path):
        """Test service run with empty directory (should do nothing)."""
        service = self._create_service(tmp_path)

        # Schedule stop after first iteration
        async def stop_after_delay():
            await asyncio.sleep(0.5)
            service.stop()

        # Run service with timeout
        asyncio.create_task(stop_after_delay())
        await asyncio.wait_for(service.run(), timeout=2.0)

        # Service should have completed
        assert not service._running

    def test_service_process_job_error_handling(self, tmp_path):
        """Test service handles job errors gracefully."""
        # This would require mocking TranscodeJob
        # Skipping for now as it requires more setup
        pass


class TestMonitorIntegration:
    """Integration tests for monitor system."""

    def test_end_to_end_flow(self, tmp_path):
        """Test complete monitoring flow (without async execution)."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create mock video file
        video_file = watch_dir / "test_video.mov"
        video_file.write_bytes(b"mock video data")

        # Create config and service
        rule = Rule(
            pattern="*.mov",
            profile="live-qlab",
            output_pattern="{filename_no_ext}_qlab.mov",
        )

        config = MonitorConfig(
            watch_directory=watch_dir,
            output_directory=output_dir,
            rules=[rule],
        )

        service = MonitorService(config)

        # Test monitoring can detect files
        new_files = service.monitor.scan()
        assert len(new_files) > 0

        # Test rules can match
        profile = service.rules.find_profile("test_video.mov")
        assert profile == "live-qlab"

        # Test output path generation
        output_path = service.rules.get_output_path(
            video_file,
            output_dir,
        )
        assert output_path is not None
        assert "test_video_qlab.mov" in str(output_path)
