import pytest
import responses
import requests
import os
from dotenv import load_dotenv
from olympiabhub.api import OlympiaAPI


@pytest.fixture
def api():
    load_dotenv()
    API_TOKEN = os.getenv("API_TOKEN")
    return OlympiaAPI(token=API_TOKEN)


@responses.activate
def test_chat_nubonyxia(api):
    model_name = "test_model"
    prompt = "test_prompt"
    expected_response = {"response": "test_response"}

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json=expected_response,
        status=200,
    )

    result = api.ChatNubonyxia(model_name, prompt)
    assert result == expected_response
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.olympia.bhub.cloud/generate"
    assert responses.calls[0].response.status_code == 200


@responses.activate
def test_chat(api):
    model_name = "test_model"
    prompt = "test_prompt"
    expected_response = {"response": "test_response"}

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json=expected_response,
        status=200,
    )

    result = api.Chat(model_name, prompt)
    assert result == expected_response
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.olympia.bhub.cloud/generate"
    assert responses.calls[0].response.status_code == 200


@responses.activate
def test_chat_nubonyxia_request_failure(api):
    model_name = "test_model"
    prompt = "test_prompt"

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(requests.exceptions.RequestException):
        api.ChatNubonyxia(model_name, prompt)


@responses.activate
def test_chat_request_failure(api):
    model_name = "test_model"
    prompt = "test_prompt"

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(requests.exceptions.RequestException):
        api.Chat(model_name, prompt)
