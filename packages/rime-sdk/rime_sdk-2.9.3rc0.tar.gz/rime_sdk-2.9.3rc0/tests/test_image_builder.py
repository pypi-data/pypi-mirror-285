"""Tests for the image builder implementations."""
import pytest

from rime_sdk.image_builder import ImageBuilder
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import (
    RimeManagedImage,
    RimeManagedImageStatus,
)


def test_image_builder_get_status_with_rpc_failure():
    """Test get status when RPC succeeds."""
    builder = ImageBuilder(
        api_client=ApiClient(),
        name="rpc_error",
    )
    with pytest.raises(ValueError):
        builder.get_status()


def test_image_builder_get_status_with_rpc_success():
    """Test get status when RPC succeeds."""
    builder = ImageBuilder(
        api_client=ApiClient(),
        name="zzy",
    )
    status = builder.get_status()
    assert (
        status
        == RimeManagedImage(
            name="zzy", status=RimeManagedImageStatus.BUILDING_FIRST_TIME
        ).to_dict()
    )


def test_image_builder_get_status_waits_until_ready():
    """Test get status when RPC succeeds."""
    builder = ImageBuilder(
        api_client=ApiClient(),
        name="beta",
    )
    status = builder.get_status(wait_until_finish=True, poll_rate_sec=0.01)
    assert (
        status
        == RimeManagedImage(name="beta", status=RimeManagedImageStatus.READY).to_dict()
    )


def test_image_builder_get_status_waits_until_failure():
    """Test get status when RPC succeeds."""
    builder = ImageBuilder(
        api_client=ApiClient(),
        name="fails",
    )
    status = builder.get_status(wait_until_finish=True, poll_rate_sec=0.01)
    assert (
        status
        == RimeManagedImage(
            name="fails", status=RimeManagedImageStatus.FAILED
        ).to_dict()
    )
