"""Tests for the generative_model module."""
import pytest

from rime_sdk import Client
from rime_sdk.swagger.swagger_client import GenerativeTestingResultExample
from rime_sdk.swagger.swagger_client import (
    GenerativeValidationApi as GenerativeModelTestingApi,
)
from rime_sdk.swagger.swagger_client import (
    GenerativevalidationGenerativeTestingResult,
    GenerativevalidationGetResultsResponse,
    GenerativevalidationObjectiveSubCategory,
    GenerativevalidationStartTestResponse,
    RimeAttackObjective,
    RimeSeverity,
    RimeUUID,
)


@pytest.fixture
def mock_start_generative_model_tests(mocker, mock_job_id):
    """Mocks responses to CreateFirewall requests."""

    def mock_function(body=None):
        if body is None:
            raise ValueError("provide a request body")

        return GenerativevalidationStartTestResponse(job_id=RimeUUID(uuid=mock_job_id))

    mocker.patch.object(
        GenerativeModelTestingApi,
        "start_generative_test",
        side_effect=mock_function,
    )


@pytest.fixture
def mock_get_generative_test_results(mocker, mock_job_id):
    """Mocks responses to GetFirewall requests."""

    def mock_function(job_id_uuid=None, page_token=None, page_size=None):
        if job_id_uuid is None:
            raise ValueError("provide a job id")

        result: GenerativevalidationGenerativeTestingResult = {
            "id": RimeUUID(uuid="p401d070-7088-4548-b7b1-6e6c291644a6"),
            "job_id": RimeUUID(uuid=mock_job_id),
            "attack_technique": "cool attack",
            "attack_objective": RimeAttackObjective.ABUSE,
            "objective_sub_category": GenerativevalidationObjectiveSubCategory.STALKING,
            "failing_examples": [
                GenerativeTestingResultExample(
                    attack_prompt="cool attack",
                    model_output="cool output",
                )
            ],
            "severity": RimeSeverity.PASS,
        }
        return GenerativevalidationGetResultsResponse(results=[result])

    mocker.patch.object(
        GenerativeModelTestingApi,
        "results",
        side_effect=mock_function,
    )


def test_start_generative_model_test(mock_start_generative_model_tests, mock_job_id):
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    job = client.generative_model.start_test("http://cool.url", "tmpl", "foo.bar.1")
    assert job.job_id == mock_job_id


def test_get_generative_model_test_results(
    mock_get_generative_test_results, mock_job_id
):
    client = Client(domain="rime.abc.com", channel_timeout=0.05)
    results = list(client.generative_model.get_results(mock_job_id))
    assert len(results) == 1
    assert results[0]["id"] == RimeUUID(uuid="p401d070-7088-4548-b7b1-6e6c291644a6")
    assert results[0]["job_id"] == RimeUUID(uuid=mock_job_id)
    assert results[0]["attack_technique"] == "cool attack"
    assert results[0]["attack_objective"] == RimeAttackObjective.ABUSE
    assert (
        results[0]["objective_sub_category"]
        == GenerativevalidationObjectiveSubCategory.STALKING
    )
    assert results[0]["failing_examples"] == [
        GenerativeTestingResultExample(
            attack_prompt="cool attack",
            model_output="cool output",
        )
    ]
    assert results[0]["severity"] == RimeSeverity.PASS
