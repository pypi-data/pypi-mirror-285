"""Test SDK classes exposed in rime_sdk.test_batch."""
import pandas as pd

from rime_sdk import TestBatch
from rime_sdk.swagger.swagger_client import ApiClient


def test_get_test_cases_result_with_no_metrics():
    """Test successfully getting all test cases that have no metrics."""
    api_client = ApiClient()
    test_batch_obj = TestBatch(api_client, "works", "unseen_categorical")
    actual = test_batch_obj.get_test_cases_df()
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
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_like=True,
    )


def test_get_test_cases_result_with_metrics():
    """Test successfully getting all test cases that have metrics."""
    api_client = ApiClient()
    test_batch_obj = TestBatch(api_client, "with metrics", "unseen_categorical")
    actual = test_batch_obj.get_test_cases_df()
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
                "FAILING_INPUTS:foo": 10.0,
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
                "FAILING_INPUTS:foo": None,
                "importance_score": 0.2,
            },
        ]
    )
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_like=True,
    )
