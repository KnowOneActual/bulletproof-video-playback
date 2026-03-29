"""Tests for the Bulletproof Video Playback API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime
from pathlib import Path

from bulletproof.api.server import api_app
from bulletproof.api.routes import set_monitor_service
from bulletproof.api.models import (
    HealthResponse, MonitorStatusResponse, QueueStatusResponse, JobResponse,
    JobStatus, RuleResponse, ConfigResponse, ConfigUpdate, ProfileResponse,
    HistoryResponse
)
from bulletproof.core.config import MonitorConfig
from bulletproof.core.rules import Rule, PatternType
from bulletproof.core.queue import QueuedJob
from bulletproof.core.profile import TranscodeProfile, BUILT_IN_PROFILES


# Fixture for a mock MonitorService
@pytest.fixture
def mock_monitor_service(mocker):
    """Provides a mock MonitorService for API testing."""
    service = MagicMock()
    # Default mock values for common methods, suitable for test_get_queue_empty
    service.get_status.return_value = {
        "running": True,
        "paused": False,
        "watch_directory": "/mock/watch",
        "output_directory": "/mock/output",
        "poll_interval": 5,
        "timestamp": datetime.now().isoformat(),
        "monitor": {"files": []},
        "queue": {
            "total_jobs": 0,
            "pending": 0,
            "processing": 0,
            "complete": 0,
            "error": 0,
        },
    }

    # Patch Path.exists and Path.is_dir for the duration of the fixture
    mocker.patch.object(Path, 'exists', lambda p: str(p) in ["/mock/watch", "/mock/output"])
    mocker.patch.object(Path, 'is_dir', lambda p: str(p) in ["/mock/watch", "/mock/output"])
    mocker.patch.object(Path, 'mkdir', MagicMock())
    
    service.config = MonitorConfig(
        watch_directory="/mock/watch",
        output_directory="/mock/output",
        poll_interval=5,
        delete_input=False,
        log_level="INFO",
        rules=[],
    )
    service.queue.get_all.return_value = []
    service.queue.get_history.return_value = []
    service.queue.get_current.return_value = None
    service.rule_engine.get_status.return_value = {"rules": []}

    def _mock_update_config(update_dict, persist=False):
        for key, value in update_dict.items():
            if key == "rules":
                updated_rules = []
                for rule_dict in value:
                    # Convert pattern_type string to PatternType enum
                    if "pattern_type" in rule_dict and isinstance(rule_dict["pattern_type"], str):
                        rule_dict["pattern_type"] = PatternType(rule_dict["pattern_type"])
                    updated_rules.append(Rule(**rule_dict))
                service.config.rules = updated_rules
            elif hasattr(service.config, key):
                setattr(service.config, key, value)
    service.update_config.side_effect = _mock_update_config

    set_monitor_service(service)
    yield service
    # Clean up after test
    set_monitor_service(None)


# Fixture for the FastAPI test client
@pytest.fixture
def client():
    """Provides a synchronous test client for the FastAPI application."""
    return TestClient(api_app)


class TestApiEndpoints:
    """Test suite for Bulletproof Video Playback API endpoints."""

    def test_health_check(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test the /health endpoint."""
        # Simulate uptime
        mock_monitor_service._start_time = datetime.now()
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        health_data = HealthResponse(**response.json())
        assert health_data.status == "healthy"
        assert health_data.version == "3.1.0"
        assert health_data.uptime_seconds is not None

    def test_get_status(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test the /status endpoint."""
        mock_monitor_service.get_status.return_value = {
            "running": True,
            "paused": False,
            "watch_directory": "/mock/watch",
            "output_directory": "/mock/output",
            "poll_interval": 10,
            "timestamp": "2026-03-29T10:00:00.000000",
            "monitor": {
                "files": [
                    {"path": "file1.mov", "status": "detected"},
                    {"path": "file2.mov", "status": "detected"},
                    {"path": "file3.mov", "status": "detected"}, # Added one more detected file
                    {"path": "file4.mov", "status": "stable"},
                    {"path": "file5.mov", "status": "processing"},
                ]
            },
        }
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        status_data = MonitorStatusResponse(**response.json())
        assert status_data.running is True
        assert status_data.watch_directory == "/mock/watch"
        assert status_data.detected_files == 3
        assert status_data.stable_files == 1
        assert status_data.processing_files == 1

    def test_get_status_service_unavailable(self, client: TestClient):
        """Test /status when MonitorService is not available."""
        set_monitor_service(None)  # Explicitly set to None
        response = client.get("/api/v1/status")
        assert response.status_code == 503
        assert "Monitor service not available" in response.json()["detail"]

    def test_pause_queue(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /queue/pause endpoint."""
        response = client.post("/api/v1/queue/pause")
        assert response.status_code == 200
        assert response.json() == {"message": "Queue paused"}
        mock_monitor_service.pause.assert_called_once()

    def test_resume_queue(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /queue/resume endpoint."""
        response = client.post("/api/v1/queue/resume")
        assert response.status_code == 200
        assert response.json() == {"message": "Queue resumed"}
        mock_monitor_service.resume.assert_called_once()

    def test_clear_queue(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /queue/clear endpoint."""
        response = client.post("/api/v1/queue/clear")
        assert response.status_code == 200
        assert response.json() == {"message": "Queue cleared"}
        mock_monitor_service.clear_queue.assert_called_once()

    def test_cancel_job_success(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /jobs/{job_id}/cancel for success."""
        mock_monitor_service.cancel_job.return_value = True
        job_id = "test_job_123"
        response = client.post(f"/api/v1/jobs/{job_id}/cancel")
        assert response.status_code == 200
        assert response.json() == {"message": f"Job '{job_id}' cancelled"}
        mock_monitor_service.cancel_job.assert_called_once_with(job_id)

    def test_cancel_job_failure(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /jobs/{job_id}/cancel for failure."""
        mock_monitor_service.cancel_job.return_value = False
        job_id = "nonexistent_job"
        response = client.post(f"/api/v1/jobs/{job_id}/cancel")
        assert response.status_code == 400
        assert f"Job '{job_id}' could not be cancelled" in response.json()["detail"]

    def test_retry_job_success(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /jobs/{job_id}/retry for success."""
        mock_monitor_service.retry_job.return_value = True
        job_id = "test_job_456"
        response = client.post(f"/api/v1/jobs/{job_id}/retry")
        assert response.status_code == 200
        assert response.json() == {"message": f"Job '{job_id}' retried"}
        mock_monitor_service.retry_job.assert_called_once_with(job_id)

    def test_retry_job_failure(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test POST /jobs/{job_id}/retry for failure."""
        mock_monitor_service.retry_job.return_value = False
        job_id = "nonexistent_job"
        response = client.post(f"/api/v1/jobs/{job_id}/retry")
        assert response.status_code == 404
        assert f"Job '{job_id}' not found" in response.json()["detail"]

    def test_get_queue_empty(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /queue when queue is empty."""
        response = client.get("/api/v1/queue")
        assert response.status_code == 200
        queue_data = QueueStatusResponse(**response.json())
        assert queue_data.total_jobs == 0
        assert queue_data.pending_jobs == 0
        assert queue_data.current_job is None
        assert queue_data.jobs == []

    def test_get_queue_with_jobs(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /queue with some jobs in various states."""
        mock_job1 = QueuedJob(
            id="job1", input_file="in1.mov", output_file="out1.mov", profile_name="p1", status=JobStatus.PENDING
        )
        mock_job2 = QueuedJob(
            id="job2", input_file="in2.mov", output_file="out2.mov", profile_name="p2", status=JobStatus.PROCESSING
        )
        mock_monitor_service.queue.get_all.return_value = [mock_job1, mock_job2]
        mock_monitor_service.queue.get_current.return_value = mock_job2
        mock_monitor_service.get_status.return_value["queue"] = {
            "total_jobs": 2, "pending": 1, "processing": 1, "complete": 0, "error": 0
        }

        response = client.get("/api/v1/queue")
        assert response.status_code == 200
        queue_data = QueueStatusResponse(**response.json())
        assert queue_data.total_jobs == 2
        assert queue_data.pending_jobs == 1
        assert queue_data.processing_jobs == 1
        assert queue_data.current_job.id == "job2"
        assert len(queue_data.jobs) == 2
        assert queue_data.jobs[0].id == "job1"
        assert queue_data.jobs[1].id == "job2"

    def test_get_history_empty(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /history when history is empty."""
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        history_data = HistoryResponse(**response.json())
        assert history_data.total_processed == 0
        assert history_data.successful == 0
        assert history_data.failed == 0
        assert history_data.jobs == []

    def test_get_history_with_jobs(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /history with some historical jobs."""
        mock_job_complete = QueuedJob(
            id="hist1", input_file="in_h1.mov", output_file="out_h1.mov", profile_name="p_h1", status=JobStatus.COMPLETE
        )
        mock_job_error = QueuedJob(
            id="hist2", input_file="in_h2.mov", output_file="out_h2.mov", profile_name="p_h2", status=JobStatus.ERROR
        )
        mock_monitor_service.queue.get_history.return_value = [mock_job_complete, mock_job_error]

        response = client.get("/api/v1/history")
        assert response.status_code == 200
        history_data = HistoryResponse(**response.json())
        assert history_data.total_processed == 2
        assert history_data.successful == 1
        assert history_data.failed == 1
        assert len(history_data.jobs) == 2
        assert history_data.jobs[0].id == "hist1"
        assert history_data.jobs[1].id == "hist2"

    def test_get_rules_empty(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /rules when no rules are configured."""
        response = client.get("/api/v1/rules")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_rules_with_rules(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /rules with some rules configured."""
        mock_rule_data = [
            {"pattern": "*.mov", "profile": "live-qlab", "output_pattern": "{filename}", "pattern_type": "glob", "priority": 100, "delete_input": True}
        ]
        mock_monitor_service.rule_engine.get_status.return_value = {"rules": mock_rule_data}

        response = client.get("/api/v1/rules")
        assert response.status_code == 200
        rules_data = [RuleResponse(**r) for r in response.json()]
        assert len(rules_data) == 1
        assert rules_data[0].pattern == "*.mov"
        assert rules_data[0].profile == "live-qlab"

    def test_get_config(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /config endpoint."""
        mock_monitor_service.config.watch_directory = "/my/watch"
        mock_monitor_service.config.output_directory = "/my/output"
        mock_monitor_service.config.log_level = "DEBUG"
        mock_monitor_service.config.rules = [
            Rule(pattern="*.mp4", profile="web-h264"),
        ]

        response = client.get("/api/v1/config")
        assert response.status_code == 200
        config_data = ConfigResponse(**response.json())
        assert config_data.watch_directory == "/my/watch"
        assert config_data.output_directory == "/my/output"
        assert config_data.log_level == "DEBUG"
        assert len(config_data.rules) == 1
        assert config_data.rules[0].pattern == "*.mp4"

    def test_patch_config_partial_update(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test PATCH /config with partial updates."""
        update_payload = {"poll_interval": 15, "log_level": "WARNING"}
        response = client.patch("/api/v1/config", json=update_payload)

        assert response.status_code == 200
        config_data = ConfigResponse(**response.json())
        assert config_data.poll_interval == 15
        assert config_data.log_level == "WARNING"
        mock_monitor_service.update_config.assert_called_once()
        # Verify call arguments match the payload and persist=False by default
        assert mock_monitor_service.update_config.call_args[0][0] == update_payload
        assert mock_monitor_service.update_config.call_args[1]["persist"] is False

    def test_patch_config_with_persist(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test PATCH /config with persist=True."""
        update_payload = {"delete_input": True}
        response = client.patch("/api/v1/config?persist=true", json=update_payload)

        assert response.status_code == 200
        config_data = ConfigResponse(**response.json())
        assert config_data.delete_input is True
        mock_monitor_service.update_config.assert_called_once()
        # Verify call arguments match the payload and persist=True
        assert mock_monitor_service.update_config.call_args[0][0] == update_payload
        assert mock_monitor_service.update_config.call_args[1]["persist"] is True

    def test_patch_config_with_rules_update(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test PATCH /config with rules update."""
        new_rules = [
            {"pattern": "*.mp4", "profile": "new-profile", "output_pattern": "{filename}.mp4", "pattern_type": "glob", "priority": 100, "delete_input": True},
        ]
        update_payload = {"rules": new_rules}
        response = client.patch("/api/v1/config", json=update_payload)

        assert response.status_code == 200
        config_data = ConfigResponse(**response.json())
        assert len(config_data.rules) == 1
        assert config_data.rules[0].pattern == "*.mp4"
        assert mock_monitor_service.update_config.call_args[0][0]["rules"] == new_rules

    def test_validate_config(self, client: TestClient):
        """Test POST /config/validate endpoint."""
        # ConfigUpdate already performs basic validation through Pydantic
        valid_config = {"log_level": "DEBUG"}
        response = client.post("/api/v1/config/validate", json=valid_config)
        assert response.status_code == 200
        assert response.json() == {"valid": True, "message": "Configuration is valid"}

        # Test with an invalid field that Pydantic should catch
        invalid_config = {"poll_interval": "not_an_int"}
        response = client.post("/api/v1/config/validate", json=invalid_config)
        assert response.status_code == 422  # Pydantic validation error

    def test_list_available_profiles(self, client: TestClient):
        """Test GET /profiles endpoint."""
        response = client.get("/api/v1/profiles")
        assert response.status_code == 200
        profiles_data = [ProfileResponse(**p) for p in response.json()]
        assert len(profiles_data) == len(BUILT_IN_PROFILES)
        # Check if a known profile exists
        assert any(p.name == "live-qlab" for p in profiles_data)

    def test_get_job_success(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /jobs/{job_id} for success."""
        test_job = QueuedJob(
            id="job_detail_1", input_file="test.mov", output_file="out.mov", profile_name="test_profile", status=JobStatus.PENDING
        )
        mock_monitor_service.queue.get_job.return_value = test_job

        response = client.get("/api/v1/jobs/job_detail_1")
        assert response.status_code == 200
        job_data = JobResponse(**response.json())
        assert job_data.id == "job_detail_1"
        assert job_data.input_file == "test.mov"
        assert job_data.status == JobStatus.PENDING

    def test_get_job_not_found(self, client: TestClient, mock_monitor_service: MagicMock):
        """Test GET /jobs/{job_id} when job is not found."""
        mock_monitor_service.queue.get_job.return_value = None

        response = client.get("/api/v1/jobs/nonexistent")
        assert response.status_code == 404
        assert "Job 'nonexistent' not found" in response.json()["detail"]