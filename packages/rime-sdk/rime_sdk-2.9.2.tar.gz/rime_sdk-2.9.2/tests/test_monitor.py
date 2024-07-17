"""Tests for the Monitor methods."""

import pytest

from rime_sdk.monitor import Monitor
from rime_sdk.swagger.swagger_client.api_client import ApiClient


def test_update_monitor_sucesss():
    """Test successful Update call."""
    monitor = Monitor(ApiClient(), "cool monitor", "cool ct", "cool project")
    monitor.update(notify=True)


def test_update_monitor_failure_no_kwargs():
    """Test not providing any keyword arguments to Update."""
    monitor = Monitor(ApiClient(), "cool monitor", "cool ct", "cool project")
    with pytest.raises(ValueError, match="Please provide at least one keyword"):
        monitor.update()


def test_list_detected_events_success(mock_project_id_uuid_1: str):
    """Test successfully listing detected events for the monitor."""
    monitor = Monitor(ApiClient(), "cool monitor", "cool ct", mock_project_id_uuid_1)
    events = list(monitor.list_detected_events())
    assert len(events) == 3


def test_list_detected_events_unknown_monitor():
    """Test sad path for listing detected events for the monitor."""
    monitor = Monitor(ApiClient(), "UNKNOWN monitor", "cool ct", "cool_project")
    with pytest.raises(ValueError):
        _ = list(monitor.list_detected_events())
