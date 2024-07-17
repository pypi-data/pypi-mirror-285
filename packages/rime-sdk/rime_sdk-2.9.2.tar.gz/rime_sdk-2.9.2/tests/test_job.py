"""Tests for the stress test job implementations."""
import sys

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from rime_sdk.job import ImageBuilderJob, Job
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import (
    JobDataStressTest,
    RimeJobData,
    RimeJobMetadata,
)
from rime_sdk.swagger.swagger_client.models import RimeJobStatus as StatedbJobStatus
from rime_sdk.swagger.swagger_client.models import (
    RimeJobType,
    RimeStressTestJobProgress,
    RimeTestRunProgress,
    RimeTestTaskStatus,
    RimeUUID,
    TestRunProgressTestBatchProgress,
)
from tests.mock_servers.mock_constants import (
    DEFAULT_AGENT,
    DEFAULT_DATETIME,
    LATEST_LOGS_OUTPUT,
)


def test_get_status_with_rpc_success():
    """Test get status when RPC succeeds."""
    job = Job(ApiClient(), "zzyz")
    status = job.get_status()
    msg_dict = RimeJobMetadata(
        job_id="zzyz",
        job_data=RimeJobData(stress=JobDataStressTest(test_run_id="foo")),
        job_type=RimeJobType.FIREWALL_BATCH_TEST,
        status=StatedbJobStatus.RUNNING,
        agent_id=RimeUUID(DEFAULT_AGENT),
        creation_time=DEFAULT_DATETIME.strftime("%H:%M %B %d, %Y"),
        running_time_secs=100,
    ).to_dict()
    del msg_dict["archived_job_logs"]
    del msg_dict["job_data"]
    assert status == msg_dict


def test_get_test_run_job_with_rpc_failure():
    """Test getting the test run job status with an RPC failure."""
    job = Job(ApiClient(), "rpc_error")
    with pytest.raises(ValueError):
        job.get_status()


def test_get_progress():
    """Test getting the progress of a job."""
    test_run = RimeTestRunProgress(
        test_batches=[
            TestRunProgressTestBatchProgress(status=RimeTestTaskStatus.COMPLETED),
            TestRunProgressTestBatchProgress(status=RimeTestTaskStatus.PENDING),
        ]
    )
    progress = RimeStressTestJobProgress(test_run=test_run)
    job_data = RimeJobData(stress=JobDataStressTest(progress=progress))
    job_metadata = RimeJobMetadata(job_data=job_data)
    job = Job(ApiClient(), "123")
    progress = job._get_progress(job_metadata)
    assert progress, "progress must not be None"
    assert progress == "1  /  2 tests completed"


def test_get_test_cases_result_with_successful_job():
    """Test successfully getting all test cases in a dataframe."""
    job = Job(ApiClient(), "zzyzx")
    job.get_status(poll_rate_sec=0.01)

    test_run_obj = job.get_test_run()
    actual = test_run_obj.get_test_cases_df()
    expected = pd.DataFrame(
        [
            {
                "test_run_id": "foo",
                "test_batch_type": "bar",
                "features": [],
                "status": "PASS",
                "severity": "NONE",
                "category": "",
                "test_category": None,
                "importance_score": 0.3,
            },
            {
                "test_run_id": "foo",
                "test_batch_type": "bar",
                "features": [],
                "status": "PASS",
                "severity": "NONE",
                "category": "",
                "test_category": None,
                "importance_score": 0.2,
            },
        ]
    )
    assert_frame_equal(
        actual,
        expected,
        check_like=True,
        check_dtype=False,
    )


def test_get_test_cases_result_with_rpc_error():
    """Test gRPC error in ListTestCases call."""
    job = Job(ApiClient(), "custom_test_run_id:rpc_error")
    job.get_status(poll_rate_sec=0.01)

    with pytest.raises(ValueError):
        test_run_obj = job.get_test_run()
        test_run_obj.get_test_cases_df()


def test_get_test_run_result_with_successful_job():
    """Test get complete dataframe of test run result."""
    job = Job(ApiClient(), "zzyzx")
    job.get_status(poll_rate_sec=0.01)

    test_run_obj = job.get_test_run()
    df = test_run_obj.get_result_df()

    # Rigorous testing for `parse_test_run_metadata` is in
    # `tests/internal/test_protobuf_parser.py`.
    assert len(df.columns) > 0


def test_get_test_run_result_with_rpc_error():
    """Test gRPC error in GetTestRun call."""
    job = Job(ApiClient(), "custom_test_run_id:rpc_error")
    job.get_status(poll_rate_sec=0.01)
    with pytest.raises(ValueError):
        test_run_obj = job.get_test_run()
        test_run_obj.get_result_df()


def test_cancel_job_with_rpc_success():
    """Test successful CancelJob call."""
    job = Job(ApiClient(), "bingbong")
    job.cancel()
    # Cancelled job should return from get_status
    job.get_status(poll_rate_sec=0.01)


def test_cancel_job_with_unsupported_job_type():
    """Test CancelJob call with unsupported type."""
    job = ImageBuilderJob(ApiClient(), "bingbong")
    with pytest.raises(ValueError):
        job.cancel()


def test_get_latest_logs_with_rpc_failure():
    """Test getting the latest logs with an RPC failure."""
    job = Job(ApiClient(), "failing_job.logs_rpc_error")
    with pytest.raises(ValueError):
        job.get_status(verbose=True, poll_rate_sec=0.01)


def test_get_logs_with_failing_job(capsys):
    """Test getting logs on a failing job"""
    job = Job(ApiClient(), "failing_job.logs_succeed")
    job.get_status(verbose=True, poll_rate_sec=0.01)
    # Capture the test output and make sure log information shows up.
    # https://stackoverflow.com/questions/26561822/pytest-capsys-checking-output-and-getting-it-reported
    out, _ = capsys.readouterr()
    sys.stdout.write(out)
    assert LATEST_LOGS_OUTPUT in out.rstrip()


def test_get_job_debug_logs_link_successfully():
    """Test archived logs successfully."""
    job = Job(ApiClient(), "failing_job.with_accessible_logs")
    assert "cool-s3-logs-url" in job.get_job_debug_logs_link()


def test_get_job_debug_logs_link_with_expired_link():
    """Test archived logs throws error job link is expired."""
    job = Job(ApiClient(), "failing_job.with_expired_logs")
    message = job.get_job_debug_logs_link()
    assert "uncool-s3-logs-url" in message
    assert "presigned url which has expired" in message
