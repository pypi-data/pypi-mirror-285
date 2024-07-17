"""Tests for the data collector methods."""
from http import HTTPStatus
from unittest.mock import patch

import pytest

from rime_sdk.data_collector import DataCollector
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    RimeStoreDatapointsResponse,
    RimeUUID,
)
from rime_sdk.swagger.swagger_client.api import DataCollectorApi
from rime_sdk.swagger.swagger_client.rest import ApiException


@pytest.fixture(scope="session", autouse=True)
def mock_store_datapoints():
    """Mocks responses to StoreDatapoints requests."""

    def store_datapoints_return_values(body, data_stream_id_uuid):
        if data_stream_id_uuid == "cool stream":
            return RimeStoreDatapointsResponse(datapoint_ids=[RimeUUID("cool dp")])
        else:
            raise ApiException(status=HTTPStatus.NOT_FOUND)

    with patch.object(
        DataCollectorApi,
        "store_datapoints",
        side_effect=store_datapoints_return_values,
    ) as mock_api:
        yield mock_api


def test_store_datapoints_valid():
    """Test storing a valid request."""
    fake_api_client = ApiClient()
    data_collector = DataCollector(fake_api_client, "cool project")
    data_collector.log_datapoints(
        "cool stream", [{"input1": "value1"}, {"input2": "value2"}]
    )


def test_store_datapoints_fails():
    """Test storing an invalid request."""
    fake_api_client = ApiClient()
    data_collector = DataCollector(fake_api_client, "cool project")
    with pytest.raises(ValueError):
        data_collector.log_datapoints(
            "bad stream", [{"input1": "value1"}, {"input2": "value2"}]
        )
