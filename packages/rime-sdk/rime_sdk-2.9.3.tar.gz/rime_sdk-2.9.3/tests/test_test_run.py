"""Tests for the test batch implementations."""
from datetime import datetime

import pandas as pd

from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.test_run import ContinuousTestRun
from rime_sdk.test_run import TestRun as TestRunSDK


def test_get_test_batch_result_with_successful_job():
    """Test successfully getting a test batch by test type."""
    test_run_obj = TestRunSDK(ApiClient(), "some_test_run_id")
    test_batch = test_run_obj.get_test_batch("unseen_categorical")
    # unpack_metrics defaults to False
    test_batch_series = test_batch.summary()
    expected = pd.Series(
        {
            "test_run_id": "james",
            "test_type": "unseen_categorical",
            "test_name": "Unseen Categorical",
            "description": "james runs fast",
            "test_category": None,
            "category": "fast James",
            "duration_in_millis": 1,
            "severity": "SEVERITY_WARNING",
            "failing_features": ["Sabiche Pita Sandwich"],
            "security_test_details": None,
            "summary_counts.total": 5,
            "summary_counts._pass": 0,
            "summary_counts.warning": 5,
            "summary_counts.fail": 0,
            "summary_counts.skip": 0,
        }
    )
    pd.testing.assert_series_equal(
        test_batch_series, expected, check_dtype=False, check_names=False
    )

    # now set unpack_metrics to True
    test_batch_series_with_metrics = test_batch.summary(True)
    assert test_batch_series_with_metrics["OUTPUT:miles run"] == 26.2


def test_get_test_cases_result_with_successful_batch():
    """Test successfully getting all test cases in a dataframe."""
    test_run_obj = TestRunSDK(ApiClient(), "works")
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
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_like=True,
    )


def test_get_test_cases_result_with_empty_batch():
    """Test successful call when there are no test cases."""
    test_run_obj = TestRunSDK(ApiClient(), "empty")
    actual = test_run_obj.get_test_cases_df()
    expected = pd.DataFrame()
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_like=True,
    )


def test_get_test_batches_success():
    """Test successful call to get test batches."""
    test_run_obj = TestRunSDK(ApiClient(), "foo")
    output = list(test_run_obj.get_test_batches())
    assert len(output) == 2
    assert output[0].test_type == "foo"
    assert output[0].test_run_id == "foo"
    assert output[1].test_type == "bar"
    assert output[1].test_run_id == "foo"


def test_get_link_for_successful_job():
    """Test get link."""
    api_client = ApiClient()
    test_run_obj = TestRunSDK(api_client, "foo")
    link = test_run_obj.get_link()
    assert link == "weapon.rime.dev/test-runs/kevin-was-here"

    test_run_obj = ContinuousTestRun(
        api_client, "foo", (datetime.today(), datetime.today())
    )
    link = test_run_obj.get_link()
    assert link == "weapon.rime.dev/ai-firewall/continuous-tests"


def test_get_test_category_results_with_successful_job():
    """Test successfully getting a test category test result."""
    test_run_obj = TestRunSDK(ApiClient(), "some_test_run_id")
    test_category_results = test_run_obj.get_category_results_df()
    expected = pd.DataFrame(
        [
            {
                "id": "shekhar",
                "severity": 2,
                "test_batch_types": ["testA", "testB"],
                "failing_test_types": ["testB"],
                "category_importance": 10,
                "risk_category": "RISK_CATEGORY_TYPE_SECURITY_RISK",
                "test_category": "TEST_CATEGORY_TYPE_ADVERSARIAL",
                "num_none_severity": 0,
                "num_low_severity": 2,
                "num_high_severity": 1,
            }
        ]
    )
    pd.testing.assert_frame_equal(
        test_category_results, expected, check_dtype=False, check_names=False
    )
