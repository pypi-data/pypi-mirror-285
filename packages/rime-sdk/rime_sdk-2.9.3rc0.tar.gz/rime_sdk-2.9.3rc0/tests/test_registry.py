"""Tests for the registration methods."""
from datetime import datetime

import pytest

from rime_sdk.registry import Registry
from rime_sdk.swagger.swagger_client import ApiClient, RegistryValidityStatus
from rime_sdk.swagger.swagger_client.models import (
    DatasetDataset,
    ModelModel,
    RegistrypredictionPrediction,
    RimeUUID,
)


@pytest.fixture
def registry_client():
    return Registry(ApiClient())


def test_register_dataset_uploaded(
    mock_register_dataset,
    registry_client,
    mock_project_id_uuid_1: str,
    mock_uploaded_dataset_id: str,
    mock_upload_path: str,
):
    """Test registering a dataset."""

    # Test no integration, but all other args
    register_dataset_response = registry_client.register_dataset(
        project_id=mock_project_id_uuid_1,
        name="dataset",
        data_config={
            "connection_info": {"data_file": {"path": mock_upload_path}},
            "data_params": {"label_col": "label"},
        },
        tags=["cool", "beast"],
        metadata={"cool_car": "tom"},
        ct_info={
            "firewall_id": "cool firewall",
            "start_time": datetime(year=2000, month=1, day=1),
            "end_time": datetime(year=2000, month=1, day=2),
        },
    )

    assert register_dataset_response == mock_uploaded_dataset_id


def test_register_dataset_integration(
    mock_register_dataset,
    registry_client,
    mock_project_id_uuid_2: str,
    mock_integration_id_uuid: str,
    mock_integration_dataset_id: str,
    mock_dataset_name_2: str,
):
    register_dataset_response = registry_client.register_dataset(
        project_id=mock_project_id_uuid_2,
        name=mock_dataset_name_2,
        data_config={
            "connection_info": {
                "data_collector": {
                    "data_stream_id": "some stream",
                }
            },
            "data_params": {"label_col": "label"},
        },
        integration_id=mock_integration_id_uuid,
        tags=["cool", "beast"],
        metadata={"cool_cat": "tom"},
    )

    assert register_dataset_response == mock_integration_dataset_id


def test_list_datasets(
    mock_list_datasets,
    registry_client,
    mock_dataset_id_1: str,
    mock_dataset_name_1: str,
    mock_dataset_id_2: str,
    mock_dataset_name_2: str,
    mock_project_id_uuid_1: str,
):
    """Test list datasets."""
    ref_datasets = [
        DatasetDataset(dataset_id=mock_dataset_id_1, name=mock_dataset_name_1),
        DatasetDataset(dataset_id=mock_dataset_id_2, name=mock_dataset_name_2),
    ]

    received_data = []
    for dataset in registry_client.list_datasets(mock_project_id_uuid_1):
        received_data.append(dataset)

    for i, dataset in enumerate(ref_datasets):
        assert received_data[i] == dataset.to_dict()


def test_list_models(
    mock_list_models,
    registry_client,
    mock_model_id_uuid_1: str,
    mock_model_name_1: str,
    mock_model_id_uuid_2: str,
    mock_model_name_2: str,
    mock_project_id_uuid_1: str,
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
    for model in registry_client.list_models(mock_project_id_uuid_1):
        received_models.append(model)

    for i, ref_model in enumerate(ref_models):
        assert received_models[i] == ref_model.to_dict()


def test_list_predictions(
    mock_list_predictions,
    registry_client,
    mock_dataset_id_1: str,
    mock_dataset_id_2: str,
    mock_model_id_uuid_2: str,
    mock_model_id_uuid_1: str,
    mock_project_id_uuid_1: str,
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
    for pred in registry_client.list_predictions(
        mock_project_id_uuid_1, dataset_id=mock_dataset_id_1
    ):
        received_preds.append(pred)

    for i, ref_pred in enumerate(ref_preds):
        assert received_preds[i] == ref_pred.to_dict()


def test_register_model(
    mock_register_model,
    registry_client,
    mock_external_id: str,
    mock_model_id_uuid_1: str,
    mock_model_name_1: str,
    mock_project_id_uuid_1: str,
    mock_external_model_id_uuid: str,
):
    """Test registering a model."""

    # Test with not external id or model info provided
    register_model_response = registry_client.register_model(
        project_id=mock_project_id_uuid_1,
        name=mock_model_name_1,
        tags=["cool", "beast"],
        metadata={"cool_mouse": "jerry"},
    )

    assert register_model_response == mock_model_id_uuid_1

    # Test with external id and model info provided
    register_model_response = registry_client.register_model(
        project_id="project",
        name="cool model",
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
    )

    assert register_model_response == mock_external_model_id_uuid


def test_register_predictions(
    mock_register_prediction,
    registry_client,
    mock_project_id_uuid_1: str,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
):
    """Test registering predictions."""
    registry_client.register_predictions(
        project_id=mock_project_id_uuid_1,
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


def test_get_dataset(
    mock_get_dataset,
    registry_client,
    mock_dataset_id_1: str,
    mock_dataset_name_1: str,
    mock_dataset_id_2: str,
    mock_dataset_name_2: str,
):
    """Test getting dataset."""
    dataset = registry_client.get_dataset(dataset_id=mock_dataset_id_1)
    ref_dataset = DatasetDataset(
        dataset_id=mock_dataset_id_1,
        name=mock_dataset_name_1,
        validity_status=RegistryValidityStatus.VALID,
    )
    assert dataset == ref_dataset.to_dict()

    new_dataset = registry_client.get_dataset(dataset_name=mock_dataset_name_2)
    ref_dataset = DatasetDataset(dataset_id=mock_dataset_id_2, name=mock_dataset_name_2)
    assert new_dataset == ref_dataset.to_dict()


def test_has_dataset_by_id(
    mock_get_dataset, registry_client, mock_dataset_id_1: str, mock_dataset_name_2
):
    """Test has dataset."""
    assert registry_client.has_dataset(dataset_id=mock_dataset_id_1)
    assert registry_client.has_dataset(dataset_name=mock_dataset_name_2)
    assert not registry_client.has_dataset(dataset_id="fake dataset")
    assert not registry_client.has_dataset(dataset_name="fake dataset name")


def test_get_model(
    mock_get_model,
    registry_client,
    mock_model_id_uuid_1: str,
    mock_model_name_1: str,
    mock_model_id_uuid_2: str,
    mock_model_name_2: str,
):
    """Test getting model."""
    model = registry_client.get_model(model_id=mock_model_id_uuid_1)
    ref_model = ModelModel(
        model_id=RimeUUID(uuid=mock_model_id_uuid_1),
        name=mock_model_name_1,
        validity_status=RegistryValidityStatus.PENDING,
        validity_status_message="",
    )
    assert model == ref_model.to_dict()

    new_model = registry_client.get_model(model_name=mock_model_name_2)
    ref_model = ModelModel(
        model_id=RimeUUID(uuid=mock_model_id_uuid_2), name=mock_model_name_2
    )
    assert new_model == ref_model.to_dict()


def test_get_predictions(
    mock_get_predictions,
    registry_client,
    mock_dataset_id_1: str,
    mock_model_id_uuid_1: str,
):
    """Test getting predictions."""
    pred = registry_client.get_predictions(
        dataset_id=mock_dataset_id_1, model_id=mock_model_id_uuid_1
    )
    ref_pred = RegistrypredictionPrediction(
        dataset_id=mock_dataset_id_1, model_id=RimeUUID(uuid=mock_model_id_uuid_1)
    )
    assert pred == ref_pred.to_dict()


def test_delete_dataset(mock_delete_dataset, registry_client, mock_dataset_id_1: str):
    """Test deleting dataset."""
    registry_client.delete_dataset(dataset_id=mock_dataset_id_1)


def test_delete_model(mock_delete_model, registry_client, mock_model_id_uuid_1):
    """Test deleting model."""
    registry_client.delete_model(model_id=mock_model_id_uuid_1)


def test_delete_predictions(
    mock_delete_predictions,
    registry_client,
    mock_model_id_uuid_1: str,
    mock_dataset_id_1: str,
):
    """Test deleting predictions."""
    registry_client.delete_predictions(
        model_id=mock_model_id_uuid_1, dataset_id=mock_dataset_id_1
    )
