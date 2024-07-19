"""Tests for the ct instance methods."""
import sys
from datetime import timedelta

import pytest

from rime_sdk.continuous_test import ContinuousTest
from rime_sdk.job import ContinuousTestJob
from rime_sdk.swagger.swagger_client import ApiClient


def test_get_ct_attributes(mock_model_id_uuid_1: str):
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    assert ct.get_bin_size() == timedelta(days=1)
    assert ct.get_model_id() == mock_model_id_uuid_1
    assert ct.get_ref_data_id() == "cool data"


def test_update_ct():
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    response = ct.update_ct("new model id", "new data id")
    assert response["firewall"]["model_id"]["uuid"] == "new model id"
    assert response["firewall"]["ref_data_id"] == "new data id"


def test_update_ct_no_fields_provided():
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    with pytest.raises(ValueError):
        ct.update_ct()


def test_update_ct_with_scheduled_ct():
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    response = ct.update_ct(
        "new model id",
        "new data id",
        scheduled_ct_eval_data_integration_id="cool integration",
        scheduled_ct_eval_data_info={
            "connection_info": {"databricks": {"table_name": "cool table"}},
            "data_params": {
                "label_col": "cool label column",
                "timestamp_col": "cool timestamp column",
            },
        },
    )
    assert response["firewall"]["model_id"]["uuid"] == "new model id"
    assert response["firewall"]["ref_data_id"] == "new data id"


def test_run_continuous_test_success(mock_get_dataset, mock_dataset_id_1, capsys):
    """Test continuous test with a successful RPC to start incremental run."""
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    job = ct.start_continuous_test(mock_dataset_id_1)
    assert job == ContinuousTestJob(ApiClient(), "cool job")
    out, _ = capsys.readouterr()
    sys.stdout.write(out)
    assert "" == out.rstrip()


def test_delete_ct():
    """Test deleting the continuous test."""
    api_client = ApiClient()
    ct = ContinuousTest(api_client, "cool ct")
    assert ct.delete_ct(force=True) is None


def test_list_monitors_bad_monitor_type():
    """Test providing a bad monitor type to the continuous test."""
    ct = ContinuousTest(ApiClient(), "cool ct")
    with pytest.raises(ValueError, match="BAGOOL is not a valid monitor type"):
        list(ct.list_monitors(monitor_types=["BAGOOL"]))


def test_list_monitors_bad_risk_category_type():
    """Test providing a bad monitor type to the continuous test."""
    ct = ContinuousTest(ApiClient(), "cool ct")
    with pytest.raises(ValueError, match="BLEH is not a valid risk category type"):
        list(ct.list_monitors(risk_category_types=["BLEH"]))


def test_list_monitors_success_no_filter():
    """Test successfully listing monitors for the continuous test."""
    ct = ContinuousTest(ApiClient(), "cool ct")
    monitors = list(ct.list_monitors())
    assert len(monitors) > 0


def test_get_link():
    """Test getting the link to the continuous test."""
    ct = ContinuousTest(ApiClient(), "cool ct")
    assert ct.get_link() == "https://rime.com/continuous-test/cool-ct"


def test_get_events_df():
    """Test getting the DataFrame of Events for the continuous test."""
    ct = ContinuousTest(ApiClient(), "cool ct")
    ct.get_events_df()
