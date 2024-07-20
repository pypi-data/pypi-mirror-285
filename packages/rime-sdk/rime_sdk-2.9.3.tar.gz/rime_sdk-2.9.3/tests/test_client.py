"""Tests for the model testing SDK."""
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union
from unittest.mock import patch

import pytest

from rime_sdk.client import Client
from rime_sdk.continuous_test import ContinuousTest
from rime_sdk.image_builder import ImageBuilder
from rime_sdk.job import FileScanJob, Job
from rime_sdk.project import ProjectInfo
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import (
    ListImagesRequestPipLibraryFilter,
    ManagedImagePipRequirement,
    RimeAgent,
    RimeJobType,
    RimeLimitStatusStatus,
    RimeManagedImage,
    RimeManagedImageStatus,
)
from tests.mock_servers.mock_constants import DEFAULT_AGENT, NON_EXISTENT_QUERY_KEY

# Simple config for testing kicking off a run
model_id = "760eca31-d95d-4472-8f22-0e02c5a55b1f"
TEST_CLI_CONFIG = {
    "data_info": {
        "ref_dataset_id": "q401d070-7088-4548-b7b1-6e6c291611a6",
        "eval_dataset_id": "y3ec600e-9074-47d6-bdcb-5a2c459eb903",
    },
    "model_id": "c301d070-3088-4128-a7b1-6e6c291611a6",
    "run_name": "placeholder run name",
}

# Simple integration variables for testing
INTEGRATION_VAR_ONE = {
    "name": "password",
    "sensitivity": "VARIABLE_SENSITIVITY_WORKSPACE_SECRET",
    "value": "abc",
}
INTEGRATION_VAR_TWO = {
    "name": "just a name",
    "sensitivity": "VARIABLE_SENSITIVITY_PUBLIC",
}
INTEGRATION_VAR_BAD_ONE = {
    "name": "oops",
}
INTEGRATION_VAR_BAD_TWO = {
    "name": "eeeeeee",
    "sensitivity": "idc",
}
FILE_SCAN_RESULT = {
    "file_scan_id": "file-scan-job",
    "project_id": "123",
    "model_id": "456",
    "file_security_reports": [
        {
            "filename": "pytorch.bin",
            "dependencies": ["pandas", "sklearn", "fairseq", "os"],
            "unexpected_dependencies": ["os", "fairseq"],
            "unsafe_dependencies": ["os"],
        },
    ],
}
CLIENT_SDK_VERSION = "2.8.1rc3+85.g932e27f08a"


def test_client_creation():
    """Test client creation."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    assert client is not None
    assert client.customer_name == "beast"


@pytest.mark.parametrize(
    "mock_get_limit_status", ["BEAST"], indirect=["mock_get_limit_status"]
)
def test_client_invalid_feature_flag():
    """Test that invalid feature flag status is surfaced to user during errors."""
    with pytest.raises(ValueError, match=r"Unexpected status value: 'BEAST'"):
        Client(domain="rime.abc.com", channel_timeout=0.05)


@pytest.mark.parametrize(
    "mock_get_limit_status",
    [RimeLimitStatusStatus.ERROR],
    indirect=["mock_get_limit_status"],
)
@pytest.mark.parametrize(
    "mock_get_rime_info",
    [{"expirationTime": datetime(2009, 11, 28)}],
    indirect=["mock_get_rime_info"],
)
def test_client_expired_license():
    """Test that expired license status is surfaced to user during errors."""
    # Check that a error message contains the word "license"
    with pytest.raises(ValueError, match=r"Your license has expired"):
        Client(domain="rime.abc.com", channel_timeout=0.05)


@pytest.mark.parametrize(
    "mock_get_rime_info",
    [
        {"clusterInfoVersion": "2.3.0rc3+15.gd719627f94"},
        {"clusterInfoVersion": "2.6.9rc3+15.gd719627f94"},
    ],
    indirect=["mock_get_rime_info"],
)
@patch("importlib_metadata.version")
def test_client_version_minor_or_major_above_server_version_throws_error(
    mock_importlib_metadata,
):
    mock_importlib_metadata.return_value = CLIENT_SDK_VERSION
    with pytest.raises(
        ValueError, match="Python SDK package is ahead of the server version."
    ):
        Client(domain="rime.abc.com", channel_timeout=0.05)


@pytest.mark.parametrize(
    "mock_get_rime_info",
    [
        {"clusterInfoVersion": "2.9.0rc3+15.gd719627f94"},
        {"clusterInfoVersion": "2.8.3rc3+15.gd719627f94"},
    ],
    indirect=["mock_get_rime_info"],
)
@patch("importlib_metadata.version")
def test_client_version_below_server_version_logs_warning(
    mock_importlib_metadata, caplog
):
    mock_importlib_metadata.return_value = CLIENT_SDK_VERSION
    with caplog.at_level(logging.WARNING):
        Client(domain="rime.abc.com", channel_timeout=0.05)
        assert "Python SDK package is behind the server version." in caplog.text


@pytest.mark.parametrize(
    "mock_get_rime_info",
    [
        {"clusterInfoVersion": "2.8.0rc3+15.gd719627f94"},
    ],
    indirect=["mock_get_rime_info"],
)
@patch("importlib_metadata.version")
def test_client_version_only_patch_version_above_server_should_not_error_or_warn(
    mock_importlib_metadata,
    caplog,
):
    """Test client creation."""
    mock_importlib_metadata.return_value = CLIENT_SDK_VERSION
    with caplog.at_level(logging.WARNING):
        Client(domain="rime.abc.com", channel_timeout=0.05)
        assert caplog.text == ""


@pytest.mark.parametrize(
    "mock_get_limit_status",
    [RimeLimitStatusStatus.ERROR],
    indirect=["mock_get_limit_status"],
)
@pytest.mark.parametrize(
    "mock_get_rime_info",
    [{"expirationTime": datetime.today()}],
    indirect=["mock_get_rime_info"],
)
def test_client_expired_license_with_grace_period(capfd):
    """Test that expired license status within the grace period (one week)
    is surfaced to user during errors."""
    Client(domain="rime.abc.com", channel_timeout=0.05)
    out, _ = capfd.readouterr()
    expected_grace_period_end = (datetime.today() + timedelta(7)).date()
    assert f"You have until {expected_grace_period_end} to upgrade" in out


def parametrize_stress_tests(test_func):
    """Decorator to parametrize stress tests."""

    @pytest.mark.parametrize(
        "stress_test_function,test_cli_config",
        [
            (Client.start_stress_test, TEST_CLI_CONFIG),
        ],
    )
    @wraps(test_func)
    def wrapper(*args, **kwargs):
        return test_func(*args, **kwargs)

    return wrapper


@parametrize_stress_tests
def test_start_stress_test_with_start_stress_test_rpc_failure(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test starting the stress test with an RPC failure to backend."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        stress_test_function(client, test_cli_config, "barack_obama.rpc_error")


@parametrize_stress_tests
def test_start_stress_test_with_nonexistent_project(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test starting a stress test when project id doesn't exist."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        stress_test_function(client, test_cli_config, "does_not_exist.joe_biden")


@parametrize_stress_tests
def test_start_stress_test_with_verify_project_id_rpc_failure(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test starting a stress test when the RPC to verify the project id errors."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        stress_test_function(client, test_cli_config, "rpc_error.mufasa")


@parametrize_stress_tests
def test_start_stress_test_with_rpc_success(
    mock_get_dataset,
    mock_get_model,
    mock_model_id_uuid_1,
    mock_dataset_id_2,
    stress_test_function,
    test_cli_config,
    capsys,
):
    """Test the stress test with a successful RPC to start the stress test."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(client, test_cli_config, "foo.bar")
    out, _ = capsys.readouterr()
    sys.stdout.write(out)
    assert "dataset validation error message" in out.rstrip()
    assert mock_dataset_id_2 in out.rstrip()
    assert f"{mock_model_id_uuid_1} is VALIDITY_STATUS_PENDING" in out.rstrip()
    assert "cool dataset 1" not in out.rstrip()
    # if error message is empty, do not print
    assert "The validation error message of the model is" not in out.rstrip()
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_custom_image(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test the stress test using a custom image specification."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "run_time_info": {
                "custom_image": {
                    "custom_image": {
                        "name": "awesome/sauce:latest",
                        "pull_secret": {"name": "good_cred"},
                    }
                }
            },
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_managed_image(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test the stress test using a managed image specification."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "run_time_info": {"custom_image": {"managed_image_name": "bloom"}},
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_custom_tests_str(stress_test_function, test_cli_config):
    """Test the stress test with a custom tests string."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "test_suite_config": {
                "custom_tests": ['{"test_path": "custom.py"}'],
                **test_cli_config,
            }
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_custom_tests_dict(
    stress_test_function, test_cli_config
):
    """Test the stress test with a custom tests dict."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "test_suite_config": {
                "custom_tests": [{"test_path": "custom.py"}],
                **test_cli_config,
            }
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_individual_tests_str(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test the stress test with a individual tests string."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "test_suite_config": {
                "individual_tests_config": '{"test_path": "custom.py"}',
            },
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_individual_tests_dict(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test the stress test with a individual tests dict."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "test_suite_config": {
                "individual_tests_config": {"test_path": "custom.py"},
            },
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


def test_start_stress_test_with_bad_config():
    """Test starting a stress test with a bad model test configuration."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        Client.start_stress_test(
            client,
            {
                "test_suite_config": {
                    "custom_tests": "not a list so this should raise an exception",
                }
            },
            "foo.bar",
        )


@parametrize_stress_tests
def test_start_stress_test_with_requests(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test starting a stress test with RAM and CPU requests specified."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "run_time_info": {
                "resource_request": {
                    "ram_request_megabytes": 5000,
                    "cpu_request_millicores": 1000,
                },
            },
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")


@parametrize_stress_tests
def test_start_stress_test_with_agent_id(
    mock_get_dataset, mock_get_model, stress_test_function, test_cli_config
):
    """Test the stress test using an agent_id specification."""
    new_agent_id: str = DEFAULT_AGENT
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = stress_test_function(
        client,
        {
            "run_time_info": {"agent_id": new_agent_id},
            **test_cli_config,
        },
        "foo.bar",
    )
    fake_api_client = ApiClient()
    assert job == Job(fake_api_client, "zzyzx")
    assert new_agent_id == job.get_agent_id()


def test_list_agents_with_rpc_success():
    """Test listing agents with successful rpc."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    listed_agents = client.list_agents()
    expected = [
        RimeAgent(name="agent1").to_dict(),
        RimeAgent(name="agent2").to_dict(),
    ]
    agents = list(listed_agents)
    # Compare the lists of dictionaries.
    assert expected == agents


def test_create_project_with_rpc_failure():
    """Test create project when rpc failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.create_project(
            name="exists",
            description="blah",
            model_task="MODEL_TASK_BINARY_CLASSIFICATION",
        )


def test_create_project_fails_with_invalid_model_task():
    """Test creating a project with invalid model task."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError, match="Invalid model task"):
        client.create_project(
            name="foo", description="The quick brown", model_task="BAD MODEL TASK"
        )


def test_create_project_with_rpc_success():
    """Test creating a project with successful rpc"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    proj = client.create_project(
        name="foo",
        description="The quick brown",
        model_task="MODEL_TASK_BINARY_CLASSIFICATION",
    )
    expected_proj_info = ProjectInfo(
        project_id="123", name="foo", description="The quick brown"
    )
    assert proj.info == expected_proj_info


def test_create_project_with_rpc_success_including_optional_params():
    """Test creating a project with successful rpc"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    proj = client.create_project(
        name="foo_optional",
        model_task="MODEL_TASK_BINARY_CLASSIFICATION",
        description="The quick brown",
        use_case="fox jumps over",
        ethical_consideration="the lazy dog",
        run_time_info={
            "custom_image": {"managed_image_name": "bloom"},
            "resource_request": {
                "ram_request_megabytes": 2,
                "cpu_request_millicores": 2,
            },
        },
    )
    expected_proj_info = ProjectInfo(
        project_id="123_optional",
        name="foo_optional",
        description="The quick brown",
        use_case="fox jumps over",
        ethical_consideration="the lazy dog",
        run_time_info={
            "custom_image": {"managed_image_name": "bloom"},
            "resource_request": {
                "ram_request_megabytes": 2,
                "cpu_request_millicores": 2,
            },
        },
    )

    assert proj.info == expected_proj_info


def test_create_project_fails_with_invalid_general_access_role():
    """Test creating a project with invalid general access role."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.create_project(
            name="foo",
            description="The quick brown",
            model_task="MODEL_TASK_BINARY_CLASSIFICATION",
            general_access_role="ACTOR_ROLE_ADMIN",
        )


def test_create_project_with_general_access_role_success():
    """Test creating a project with valid general access role"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    proj = client.create_project(
        name="foo",
        description="The quick brown",
        model_task="MODEL_TASK_BINARY_CLASSIFICATION",
        general_access_role="ACTOR_ROLE_USER",
    )
    expected_proj_info = ProjectInfo(
        project_id="123", name="foo", description="The quick brown"
    )
    assert proj.info == expected_proj_info
    proj_general_access_roles = proj.get_general_access_roles()
    expected_parent_role_roles = {
        "Workspace Role: ACTOR_ROLE_USER": "Project Role:ACTOR_ROLE_USER",
        "Workspace Role: ACTOR_ROLE_VIEWER": "Project Role:ACTOR_ROLE_VIEWER",
        "Workspace Role: ACTOR_ROLE_VP": "Project Role:ACTOR_ROLE_USER",
        "Workspace Role: ACTOR_ROLE_ADMIN": "Project Role:ACTOR_ROLE_USER",
    }
    assert len(proj_general_access_roles.keys()) == len(
        expected_parent_role_roles.keys()
    )
    for parent_role in expected_parent_role_roles:
        assert (
            proj_general_access_roles[parent_role]
            == expected_parent_role_roles[parent_role]
        )


def test_get_project_with_rpc_success():
    """Test getting a project with successful rpc."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    proj = client.create_project(
        name="foo",
        description="The quick brown",
        model_task="MODEL_TASK_BINARY_CLASSIFICATION",
    )
    getted_proj = client.get_project(proj.project_id)
    expected_proj_info = ProjectInfo(
        project_id="123", name="foo", description="The quick brown"
    )
    assert getted_proj.info == expected_proj_info


def test_delete_project_with_rpc_success():
    """Test deleting a project with successful rpc."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    proj = client.create_project(
        name="foo",
        description="The quick brown",
        model_task="MODEL_TASK_BINARY_CLASSIFICATION",
    )
    client.delete_project(proj.project_id, force=True)


def test_create_managed_image_with_rpc_failure():
    """Tests creating an image with an RPC failure."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.create_managed_image(
            name="exists",
            requirements=[
                ManagedImagePipRequirement(name="bar", version_specifier="===2.0.0")
            ],
        )


def test_create_managed_image_with_rpc_success():
    """Tests creating an image with an RPC success."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = client.create_managed_image(
        name="foo",
        requirements=[
            ManagedImagePipRequirement(name="bar", version_specifier="===2.0.0")
        ],
        package_requirements=[
            Client.os_requirement(name="baz", version_specifier="6.5.9")
        ],
    )
    fake_api_client = ApiClient()
    assert job == ImageBuilder(
        fake_api_client,
        "foo",
    )


def test_delete_managed_image_with_rpc_success():
    """Tests deleting an image with an RPC success."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    client.delete_managed_image("foo")


def test_delete_managed_image_which_does_not_exist():
    """Tests deleting an image with an RPC success when DNE."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError, match="Docker image with name DNE does not exist."):
        client.delete_managed_image("DNE")


def test_list_managed_images_with_rpc_failure():
    """Tests listing images with an RPC failure."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)

    # Since we have an iterator, a ValueError is only surfaced
    # when we yield a result
    with pytest.raises(ValueError):
        listed_images = client.list_managed_images(
            pip_library_filters=[client.pip_library_filter("rpc_error")]
        )
        _ = list(listed_images)


def test_list_managed_images_with_rpc_success():
    """Tests listing images with an RPC success."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    listed_images = client.list_managed_images()
    expected = [
        RimeManagedImage(name="beta", status=RimeManagedImageStatus.READY).to_dict(),
        RimeManagedImage(
            name="alpha",
            status=RimeManagedImageStatus.BUILDING_FIRST_TIME,
        ).to_dict(),
    ]

    images = list(listed_images)
    # Compare the lists of dictionaries ignoring the order.
    assert sorted(expected, key=lambda x: x["name"]) == sorted(
        images, key=lambda x: x["name"]
    )


def test_get_managed_images():
    """Tests getting images."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    expected = RimeManagedImage(
        name="beta", status=RimeManagedImageStatus.READY
    ).to_dict()
    image = client.get_managed_image("beta")
    # Compare the lists of dictionaries ignoring the order.
    assert expected == image


def test_has_managed_images():
    """Tests getting images."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    has_image = client.has_managed_image("beta", check_status=True)
    assert has_image
    has_image = client.has_managed_image("alpha", check_status=True)
    assert not has_image
    has_image = client.has_managed_image("nope")
    assert not has_image


def test_pip_requirement_with_good_specification():
    """Tests constructing a pip requirement with good args."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    req = client.pip_requirement("tensorflow", "")
    assert req == ManagedImagePipRequirement(name="tensorflow", version_specifier="")


def test_pip_requirement_with_bad_specification():
    """Tests constructing a pip requirement with bad args."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.pip_requirement("tensorflow", 5)


def test_pip_library_filter_with_good_specification():
    """Tests constructing a pip library filter with good args."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    req = client.pip_library_filter("tensorflow")
    assert req == ListImagesRequestPipLibraryFilter(name="tensorflow")
    assert not req.version


def test_pip_library_filter_with_bad_specification():
    """Tests constructing a pip library filter with bad args."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.pip_library_filter("tensorflow", 5)


def test_get_ct_from_project(mock_project_id_uuid_1: str):
    """Test getting a continous test using project id."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    ct = client.get_ct_for_project(mock_project_id_uuid_1)
    fake_api_client = ApiClient()
    assert ct == ContinuousTest(fake_api_client, "cool ct")


def test_upload_dataset_file_invalid_upload_path():
    """Test the `upload_dataset_file` when a failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    # Call the upload.
    with pytest.raises(
        ValueError,
        match=r"specified upload_path must not be an empty string",
    ):
        client.upload_file("foo", "")


def test_upload_dataset_file_fails():
    """Test the `upload_dataset_file` when a failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_dataset_file"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.side_effect = ValueError("upload failed")

        # Call the upload.
        with pytest.raises(ValueError, match=r"upload failed"):
            client.upload_file("foo")

        # Check the mocks' invocations.
        mock.assert_called_once_with(Path("foo"), None)


def test_upload_dataset_file_succeeds():
    """Test the `upload_dataset_file` when uploading succeeds."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_dataset_file"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = "foo.com/bar"

        # Call the upload.
        assert client.upload_file(Path("bar")) == "foo.com/bar"

        # Check the mocks' invocations.
        mock.assert_called_once_with(Path("bar"), None)


def test_delete_uploaded_file_url_succeeds():
    """Test the `delete_uploaded_file_url` succeeding"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.delete_uploaded_file_url"
    ) as mock:
        mock.return_value = None
        assert not client.delete_uploaded_file_url("some_url")
        mock.assert_called_once()


def test_list_uploaded_file_urls_succeeds():
    """Test the `list_uploaded_file_urls` succeeding"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    file_urls = ["files/file1.txt", "files/file2.txt"]
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.list_uploaded_files_urls"
    ) as mock:
        mock.return_value = file_urls
        assert client.list_uploaded_file_urls() == file_urls
        mock.assert_called_once()


def test_upload_dataset_file_with_upload_path_succeeds():
    """Test the `upload_dataset_file` with upload_path when uploading succeeds."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_dataset_file"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = "foo.com/bar"

        # Call the upload.
        assert client.upload_file(Path("bar"), "up") == "foo.com/bar"

        # Check the mocks' invocations.
        mock.assert_called_once_with(Path("bar"), "up")


def test_upload_model_directory_invalid_upload_path():
    """Test the `upload_model_directory` when a failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)

    # Call the upload.
    with pytest.raises(
        ValueError,
        match=r"specified upload_path must not be an empty string",
    ):
        client.upload_directory("foo", upload_path="")


def test_upload_model_directory_fails():
    """Test the `upload_model_directory` when a failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_model_directory"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.side_effect = ValueError("upload failed")

        # Call the upload.
        with pytest.raises(ValueError, match=r"upload failed"):
            client.upload_directory("foo")

        # Check the mocks' invocations.
        mock.assert_called_once_with(
            Path("foo"),
            upload_hidden=False,
            upload_path=None,
        )


def test_upload_model_directory_succeeds():
    """Test the `upload_model_directory` when uploading succeeds."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_model_directory"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = "foo.com/bar"

        # Call the upload.
        assert client.upload_directory(Path("bar"), upload_hidden=True) == "foo.com/bar"

        # Check the mocks' invocations.
        mock.assert_called_once_with(
            Path("bar"),
            upload_hidden=True,
            upload_path=None,
        )


def test_upload_model_directory_wth_upload_path_succeeds():
    """Test the `upload_model_directory` when uploading succeeds."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_model_directory"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = "foo.com/bar"

        # Call the upload.
        assert (
            client.upload_directory(Path("bar"), upload_hidden=True, upload_path="up")
            == "foo.com/bar"
        )

        # Check the mocks' invocations.
        mock.assert_called_once_with(
            Path("bar"),
            upload_hidden=True,
            upload_path="up",
        )


def _mock_upload_file(
    self, file_path: Union[Path, str], upload_path: Optional[str] = None
) -> str:
    """Mock the `upload_file` method."""
    prefix = f"{upload_path}/" if upload_path is not None else ""
    return f"s3://{prefix}{file_path}"


@patch("rime_sdk.client.Client.upload_file", _mock_upload_file)
@patch("rime_sdk.client.Path.exists", lambda _: True)
def test_upload_local_image_dataset_file_succeeds(caplog: pytest.CaptureFixture):
    """Test the upload_local_image_dataset_file with multiple image features."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    data = [
        {"image_0": "foo", "image_1": "bar", "image_2": "baz"},
        {"image_0": None, "image_2": "baz"},
    ]
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir).absolute() / "data.json"
        with open(file_path, "w") as f:
            json.dump(data, f)
        with caplog.at_level(logging.WARNING):
            new_data, new_path = client.upload_local_image_dataset_file(
                file_path, ["image_0", "image_1"], upload_path="coolguy"
            )
    assert re.match(f"s3://coolguy/.+/{file_path.name}", new_path) is not None
    assert re.match("s3://coolguy/.+/foo", new_data[0]["image_0"]) is not None
    assert re.match("s3://coolguy/.+/bar", new_data[0]["image_1"]) is not None
    assert new_data[1] == data[1]
    assert all(
        f"Found 1 null paths for feature {col}." in caplog.text
        for col in ["image_0", "image_1"]
    )
    assert "image_2" not in caplog.text


def test_get_test_run_succeeds():
    """Test the get_test_run with a valid id."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    test_run_object = client.get_test_run("found")
    assert test_run_object._test_run_id == "found"


def test_get_test_run_fails():
    """Test the get_test_run with an invalid id."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.get_test_run(NON_EXISTENT_QUERY_KEY)


def test_get_job_stress_test():
    """Test getting a stress test job."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = client.get_job("stress test")
    assert job.job_id == "stress test"
    assert job.job_type == RimeJobType.MODEL_STRESS_TEST


def test_get_job_continuous_test():
    """Test getting a continuous testing job."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = client.get_job("foo")
    assert job.job_id == "foo"
    assert job.job_type == RimeJobType.FIREWALL_BATCH_TEST


def test_get_job_not_found():
    """Test getting a job that doesn't exist."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.get_job("not found")


def test_start_file_scan():
    """Test the start_file_scan command."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = client.start_file_scan(project_id="123", model_id="456")
    fake_api_client = ApiClient()
    assert job == FileScanJob(fake_api_client, "file-scan-job")
    status = job.get_status()
    assert status["job_id"] == "file-scan-job"
    assert status["job_type"] == "JOB_TYPE_FILE_SCAN"


def test_get_file_scan_result():
    """Test the get_file_scan_result command."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    file_scan_result = client.get_file_scan_result(file_scan_id="123")
    assert file_scan_result["file_scan_id"] == FILE_SCAN_RESULT["file_scan_id"]
    assert file_scan_result["model_id"] == FILE_SCAN_RESULT["model_id"]
    assert (
        file_scan_result["file_security_reports"][0]["dependencies"]
        == FILE_SCAN_RESULT["file_security_reports"][0]["dependencies"]
    )


def test_list_file_scan_results():
    """Test listing file scan results with successful RPC calls"""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    file_scan_results = list(client.list_file_scan_results(project_id="123"))
    assert len(file_scan_results) == 1
    assert file_scan_results[0]["file_scan_id"] == FILE_SCAN_RESULT["file_scan_id"]
    assert file_scan_results[0]["model_id"] == FILE_SCAN_RESULT["model_id"]
    assert (
        file_scan_results[0]["file_security_reports"][0]["dependencies"]
        == FILE_SCAN_RESULT["file_security_reports"][0]["dependencies"]
    )


def test_delete_file_scan_result():
    """Test the delete_file_scan_result command."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    client.delete_file_scan_result(file_scan_id="123")


def test_create_integration_with_rpc_failure():
    """Test create integration when rpc failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError):
        client.create_integration(
            workspace_id="456",
            name="foo_failure",
            integration_type="INTEGRATION_TYPE_CUSTOM",
            integration_schema=[INTEGRATION_VAR_ONE],
        )


def test_create_integration_with_rpc_success():
    """Test create integration when rpc failure occurs."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    integration_id = client.create_integration(
        workspace_id="456",
        name="foo",
        integration_type="INTEGRATION_TYPE_CUSTOM",
        integration_schema=[INTEGRATION_VAR_ONE, INTEGRATION_VAR_TWO],
    )
    assert integration_id == "123"


@pytest.mark.parametrize(
    "variable,error_str",
    [
        (INTEGRATION_VAR_BAD_ONE, 'Missing key "sensitivity"'),
        (INTEGRATION_VAR_BAD_TWO, "Invalid variable sensitivity"),
    ],
)
def test_create_integration_with_bad_variable(variable, error_str):
    """Test create integration fails when bad variable provided."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError, match=error_str):
        client.create_integration(
            workspace_id="456",
            name="foo",
            integration_type="INTEGRATION_TYPE_CUSTOM",
            integration_schema=[variable],
        )


def test_create_integration_with_bad_integration_type():
    """Test create integration fails when bad integration type provided."""
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    with pytest.raises(ValueError, match="Invalid integration type"):
        client.create_integration(
            workspace_id="456",
            name="foo",
            integration_type="",
            integration_schema=[INTEGRATION_VAR_ONE],
        )
