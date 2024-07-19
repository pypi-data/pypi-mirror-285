"""Tests for project implementations."""
from datetime import timedelta
from unittest.mock import patch

import pytest

from rime_sdk import ContinuousTest, Project
from rime_sdk.job import Job
from rime_sdk.swagger.swagger_client import ApiClient, RegistryValidityStatus
from rime_sdk.swagger.swagger_client.api import NotificationSettingApi
from rime_sdk.swagger.swagger_client.models import (
    DatasetDataset,
    ModelModel,
    RegistrypredictionPrediction,
    RimeUUID,
)
from tests.mock_servers.mock_constants import NON_EXISTENT_QUERY_KEY


@pytest.fixture
def api_client() -> ApiClient:
    """Returns an api client."""
    return ApiClient()


@pytest.fixture
def project(api_client: ApiClient, mock_project_id_uuid_1) -> Project:
    """Returns a project object."""
    return Project(api_client, mock_project_id_uuid_1)


def test_list_stress_testing_jobs_rpc_success(api_client: ApiClient):
    """Test listing jobs with successful RPC call."""
    project = Project(api_client, "proj")
    jobs = project.list_stress_testing_jobs()
    assert list(jobs) == [
        Job(api_client, "beowulf"),
    ]


def test_list_scheduled_ct_jobs_rpc_success(api_client: ApiClient):
    """Test listing Scheduled CT jobs with successful RPC call."""
    project = Project(api_client, "proj")
    jobs = project.list_scheduled_ct_jobs()

    job = next(jobs)
    assert job.job_id == "ct job"
    assert job.get_test_run_ids() == ["ct1", "ct2"]

    with pytest.raises(StopIteration):
        job = next(jobs)


def test_create_ct(api_client: ApiClient, project: Project, mock_model_id_uuid_1: str):
    """Test creating a continuous test successfully."""
    ct = project.create_ct(
        mock_model_id_uuid_1,
        "cool dataset",
        timedelta(hours=2),
    )
    assert ct == ContinuousTest(api_client, "cool ct")


def test_create_scheduled_ct(
    api_client: ApiClient, project: Project, mock_model_id_uuid_1: str
):
    """Test creating scheduled CT successfully."""
    ct = project.create_ct(
        mock_model_id_uuid_1,
        "cool dataset",
        timedelta(hours=2),
        scheduled_ct_eval_data_integration_id="cool integration",
        scheduled_ct_eval_data_info={
            "connection_info": {"databricks": {"table_name": "cool table"}},
            "data_params": {
                "label_col": "cool label column",
                "timestamp_col": "cool timestamp column",
            },
        },
        scheduled_ct_eval_pred_integration_id="cool integration",
        scheduled_ct_eval_pred_info={
            "connection_info": {"databricks": {"table_name": "cool table"}},
            "pred_params": {"pred_col": "cool prediction column"},
        },
    )
    assert ct == ContinuousTest(api_client, "cool ct")


def test_create_ct_fails(mock_model_id_uuid_1: str):
    """Test when creating a continuous test fails."""
    api_client = ApiClient()
    project = Project(api_client, "fake project")
    with pytest.raises(ValueError):
        project.create_ct(mock_model_id_uuid_1, "cool ct", timedelta(hours=2))


def test_get_ct_from_project(
    api_client: ApiClient, project: Project, mock_project_id_uuid_1: str
):
    """Test getting a continuous test using project id."""
    project = Project(api_client, mock_project_id_uuid_1)
    ct = project.get_ct()
    assert ct == ContinuousTest(api_client, "cool ct")


def test_get_ct_from_project_fails():
    """Test getting a continuous test with project id fails when rpc fails."""
    api_client = ApiClient()
    project = Project(api_client, "bad project")
    with pytest.raises(ValueError):
        project.get_ct()


def test_get_ct_from_project_not_found():
    """Test getting a continuous test with project id fails when not found."""
    api_client = ApiClient()
    project = Project(api_client, "project not found")
    with pytest.raises(ValueError):
        project.get_ct()


def test_delete_ct(project: Project):
    """Test deleting a continuous test successfully."""
    project.delete_ct(force=True)


def test_delete_nonexistent_ct():
    """Test deleting a continuous test when it does not exist."""
    api_client = ApiClient()
    project = Project(api_client, "delete not found")
    with pytest.raises(ValueError, match="No continuous test found for given project."):
        project.delete_ct(force=True)


def test_list_test_runs_empty(project: Project):
    """Test listing test runs when none exist."""
    res = list(project.list_test_runs())
    assert len(res) == 0


def test_list_test_runs_exist():
    """Test listing test runs when some exist."""
    api_client = ApiClient()
    project = Project(api_client, "foo")
    res = list(project.list_test_runs())
    assert len(res) == 2
    assert res[0].test_run_id == "123"
    assert res[1].test_run_id == "bar"


def test_has_ct_true(project: Project):
    """Test checking whether a project has a continuous test when true."""
    output = project.has_ct()
    assert output


def test_has_ct_false():
    """Test checking whether a project has a continuous test when false."""
    api_client = ApiClient()
    project = Project(api_client, "continuous test not found")
    output = project.has_ct()
    assert not output


def test_get_notification_settings():
    """Test get notification settings for a project."""
    api_client = ApiClient()
    project = Project(api_client, "proj_1")
    out = project.get_notification_settings()
    assert "Job_Action" in out.keys()
    assert "wendy" in out["Job_Action"]["emails"]
    # check for non-existing project
    project = Project(api_client, NON_EXISTENT_QUERY_KEY)
    out = project.get_notification_settings()
    assert out == {}


def check_mask_side_effect(body, notification_id_uuid):
    mask = body["mask"]
    assert "emails" in mask
    assert len(notification_id_uuid) > 0


def test_add_email():
    """Test add email function from a project's notification setting."""
    api_client = ApiClient()

    with patch.object(
        NotificationSettingApi,
        "update_notification",
        side_effect=check_mask_side_effect,
    ):
        project = Project(api_client, "proj_1")

        project.add_email("newEmail@proj1.com", "Job_Action")
        # If the email is empty, method should return a value error
        with pytest.raises(ValueError):
            project.add_email("", "Job_Action")


def test_remove_email():
    """Test remove email function from a project's notification setting."""
    api_client = ApiClient()
    project = Project(api_client, "proj_1")
    project.remove_email("abc@proj1.com", "Job_Action")
    # If the email is empty, method should return a value error
    with pytest.raises(ValueError):
        project.remove_email("", "Job_Action")


def test_add_webhook():
    """Test add webhook function from a project's notification setting."""
    api_client = ApiClient()
    project = Project(api_client, "proj 1")
    project.add_webhook("newWebhook1.com", "Monitoring")
    # If the email is empty, method should return a value error
    with pytest.raises(ValueError):
        project.add_webhook("", "Monitoring")


def test_remove_webhook():
    """Test remove webhook function from a project's notification setting."""
    api_client = ApiClient()
    project = Project(api_client, "proj 1")
    # this call should not delete webhook1.com from the job_action notif setting
    project.remove_webhook("webhook1.com", "Monitoring")
    # If the email is empty, method should return a value error
    with pytest.raises(ValueError):
        project.remove_webhook("", "Monitoring")


def test_successful_get_link_for_project():
    """Test get link."""
    api_client = ApiClient()
    project = Project(api_client, "123")
    link = project.get_link()
    assert link == "https://rime.com/project/123"


def test_register_dataset(
    api_client: ApiClient,
    project: Project,
    mock_register_dataset,
    mock_uploaded_dataset_id: str,
    mock_upload_path: str,
):
    """Test register dataset."""
    dataset_id = project.register_dataset(
        name="dataset",
        data_config={
            "connection_info": {"data_file": {"path": mock_upload_path}},
            "data_params": {"label_col": "label"},
        },
        integration_id="secret integration",
        tags=["cool", "beast"],
        metadata={"cool_car": "tom"},
    )

    assert dataset_id == mock_uploaded_dataset_id


def test_register_dataset_from_file(
    mock_register_dataset,
    project: Project,
    mock_integration_id_uuid: str,
    mock_dataset_id_1: str,
):
    """Test register dataset from file."""
    dataset_id = project.register_dataset_from_file(
        name="dataset",
        remote_path="file",
        data_params={"label_col": "label"},
        integration_id=mock_integration_id_uuid,
        tags=["cool", "beast"],
        metadata={"cool_car": "tom"},
    )

    assert dataset_id == mock_dataset_id_1


def test_upload_and_register_dataset_from_file(
    mock_register_dataset,
    mock_upload_path: str,
    mock_uploaded_dataset_id: str,
    project: Project,
):
    """Test register dataset from file."""
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_dataset_file"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = mock_upload_path
        dataset_id = project.upload_and_register_dataset_from_file(
            name="dataset",
            file_path=mock_upload_path,
            data_params={"label_col": "label"},
            integration_id="secret integration",
            tags=["cool", "beast"],
            metadata={"cool_car": "tom"},
        )

    assert dataset_id == mock_uploaded_dataset_id


def test_register_model(
    mock_register_model,
    mock_integration_id_uuid: str,
    mock_external_model_id_uuid: str,
    mock_external_id: str,
):
    """Test register predictions."""
    api_client = ApiClient()
    project = Project(api_client, "project")
    model_id = project.register_model(
        name=mock_external_model_id_uuid,
        model_config={
            "hugging_face": {
                "model_uri": "ur-i mom",
                "kwargs": {
                    "tokenizer_uri": "bert or nothing",
                    "class_map": "mukil",
                    "ignore_class_names": True,
                },
            }
        },
        tags=["cool", "beast"],
        metadata={"cool_mouse": "jerry"},
        external_id=mock_external_id,
        integration_id=mock_integration_id_uuid,
        model_endpoint_integration_id="secret integration 2",
    )

    assert model_id == mock_external_model_id_uuid


def test_register_model_from_path(
    mock_register_model,
    mock_integration_id_uuid: str,
    mock_model_path_id_uuid: str,
    mock_model_path_path: str,
):
    """Test registering model using the helper function."""
    api_client = ApiClient()
    project = Project(api_client, "project")
    model_id = project.register_model_from_path(
        name="cool model",
        remote_path=mock_model_path_path,
        tags=["cool", "beast"],
        metadata={"cool_mouse": "jerry"},
        external_id="external id",
        integration_id=mock_integration_id_uuid,
        model_endpoint_integration_id="not so secret integration 2",
    )

    assert model_id == mock_model_path_id_uuid


def test_upload_and_register_model_from_path(
    mock_register_model,
    project: Project,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
):
    """Test register dataset from file."""
    with patch(
        "rime_sdk.internal.file_upload.FileUploadModule.upload_dataset_file"
    ) as mock:
        # Instantiate the mocks' behaviors.
        mock.return_value = "cool uploaded path"
        model_id = project.upload_and_register_model_from_path(
            name=mock_dataset_id_1,
            file_path="cool local file",
            tags=["cool", "beast"],
            metadata={"cool_car": "tom"},
        )

    assert model_id == mock_model_id_uuid_1


def test_register_predictions(
    project: Project,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
    mock_register_prediction,
):
    """Test register predictions."""
    project.register_predictions(
        dataset_id=mock_dataset_id_1,
        pred_config={
            "connection_info": {
                "databricks": {
                    "table_name": "craps",
                }
            },
            "pred_params": {"pred_col": "preds"},
        },
        model_id=mock_model_id_uuid_1,
        tags=["cool", "beast"],
        metadata={"cool_guy": "jeff"},
    )


def test_register_predictions_from_file(
    mock_register_prediction,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
    project: Project,
):
    """Test register predictions from file."""
    project.register_predictions_from_file(
        dataset_id=mock_dataset_id_1,
        remote_path="file",
        pred_params={"pred_col": "preds"},
        model_id=mock_model_id_uuid_1,
        tags=["cool", "beast"],
        metadata={"cool_guy": "jeff"},
    )


def test_list_datasets(
    mock_list_datasets,
    mock_dataset_id_1: str,
    mock_dataset_name_1: str,
    mock_dataset_id_2: str,
    mock_dataset_name_2: str,
    project: Project,
):
    """Test list datasets."""

    ref_datasets = [
        DatasetDataset(dataset_id=mock_dataset_id_1, name=mock_dataset_name_1),
        DatasetDataset(dataset_id=mock_dataset_id_2, name=mock_dataset_name_2),
    ]

    received_data = []
    for dataset in project.list_datasets():
        received_data.append(dataset)

    for i, dataset in enumerate(ref_datasets):
        assert received_data[i] == dataset.to_dict()


def test_list_models(
    mock_list_models,
    mock_model_id_uuid_1: str,
    mock_model_id_uuid_2: str,
    mock_model_name_1: str,
    mock_model_name_2: str,
    project: Project,
):
    """Test list models."""
    ref_models = [
        ModelModel(
            model_id=RimeUUID(uuid=mock_model_id_uuid_1), name=mock_model_name_1
        ),
        ModelModel(
            model_id=RimeUUID(uuid=mock_model_id_uuid_2), name=mock_model_name_2
        ),
    ]

    received_models = []
    for model in project.list_models():
        received_models.append(model)

    for i, ref_model in enumerate(ref_models):
        assert received_models[i] == ref_model.to_dict()


def test_list_predictions(
    mock_list_predictions,
    mock_dataset_id_1: str,
    mock_dataset_id_2: str,
    mock_model_id_uuid_1: str,
    mock_model_id_uuid_2: str,
    project: Project,
):
    """Test list predictions."""
    ref_preds = [
        RegistrypredictionPrediction(
            dataset_id=mock_dataset_id_1, model_id=RimeUUID(uuid=mock_model_id_uuid_1)
        ),
        RegistrypredictionPrediction(
            dataset_id=mock_dataset_id_2, model_id=RimeUUID(uuid=mock_model_id_uuid_2)
        ),
    ]

    received_preds = []
    for pred in project.list_predictions(dataset_id=mock_dataset_id_1):
        received_preds.append(pred)

    for i, ref_pred in enumerate(ref_preds):
        assert received_preds[i] == ref_pred.to_dict()


def test_get_dataset(
    mock_get_dataset,
    mock_dataset_id_1: str,
    mock_dataset_name_1: str,
    mock_dataset_id_2: str,
    mock_dataset_name_2: str,
    project: Project,
):
    """Test getting dataset."""
    dataset = project.get_dataset(dataset_id=mock_dataset_id_1)
    ref_dataset = DatasetDataset(
        dataset_id=mock_dataset_id_1,
        name=mock_dataset_name_1,
        validity_status=RegistryValidityStatus.VALID,
    )
    assert dataset == ref_dataset.to_dict()

    new_dataset = project.get_dataset(dataset_name=mock_dataset_name_2)
    ref_dataset = DatasetDataset(dataset_id=mock_dataset_id_2, name=mock_dataset_name_2)
    assert new_dataset == ref_dataset.to_dict()


def test_get_model(
    mock_get_model,
    mock_model_id_uuid_1: str,
    mock_model_name_1: str,
    mock_model_id_uuid_2: str,
    mock_model_name_2: str,
    project: Project,
):
    """Test getting model."""
    model = project.get_model(model_id=mock_model_id_uuid_1)
    ref_model = ModelModel(
        model_id=RimeUUID(uuid=mock_model_id_uuid_1),
        name=mock_model_name_1,
        validity_status=RegistryValidityStatus.PENDING,
        validity_status_message="",
    )
    assert model == ref_model.to_dict()

    new_model = project.get_model(model_name=mock_model_name_2)
    ref_model = ModelModel(
        model_id=RimeUUID(uuid=mock_model_id_uuid_2), name=mock_model_name_2
    )
    assert new_model == ref_model.to_dict()


def test_get_predictions(
    mock_get_predictions,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
    project: Project,
):
    """Test getting predictions."""
    pred = project.get_predictions(
        dataset_id=mock_dataset_id_1, model_id=mock_model_id_uuid_1
    )
    ref_pred = RegistrypredictionPrediction(
        dataset_id=mock_dataset_id_1, model_id=RimeUUID(uuid=mock_model_id_uuid_1)
    )
    assert pred == ref_pred.to_dict()


def test_delete_dataset(mock_delete_dataset, mock_dataset_id_1: str, project: Project):
    """Test deleting dataset."""
    project.delete_dataset(dataset_id=mock_dataset_id_1)


def test_delete_model(mock_delete_model, mock_model_id_uuid_1: str, project: Project):
    """Test deleting model."""
    project.delete_model(model_id=mock_model_id_uuid_1)


def test_delete_predictions(
    mock_delete_predictions,
    mock_model_id_uuid_1: str,
    mock_dataset_id_1: str,
    project: Project,
):
    """Test deleting predictions."""
    project.delete_predictions(
        model_id=mock_model_id_uuid_1, dataset_id=mock_dataset_id_1
    )


def test_update_stress_test_categories(project: Project):
    """Test updating stress test categories."""
    project.update_stress_test_categories(
        ["TEST_CATEGORY_TYPE_ADVERSARIAL", "TEST_CATEGORY_TYPE_BIAS_AND_FAIRNESS"]
    )


def test_update_ct_categories(project: Project):
    """Test updating continuous test categories."""
    project.update_ct_categories(
        ["TEST_CATEGORY_TYPE_ADVERSARIAL", "TEST_CATEGORY_TYPE_BIAS_AND_FAIRNESS"]
    )


def test_update_model_profiling_config(project: Project):
    """Test updating the model profiling config."""
    project.update_model_profiling_config({"nrows_for_summary": 101})


def test_update_data_profiling_config(project: Project):
    """Test updating the data profiling config."""
    project.update_data_profiling_config(
        {"column_type_info": {"allow_float_unique": True}}
    )


def test_update_test_suite_config(project: Project):
    """Test updating the test suite config."""
    project.update_test_suite_config(
        {"individual_tests_config": {"feat_subset_f1": {"min_sample_size": 30}}}
    )


def test_update_run_time_info(project: Project):
    """Test updating the run time info."""
    project.update_run_time_info({"run_time_info": {"random_seed": 123}})
