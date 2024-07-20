import pytest
import responses
import requests
from dotenv import load_dotenv
from olympiabhub import OlympiaAPI


@pytest.fixture
def api():
    load_dotenv()
    model_name = "test_model"
    return OlympiaAPI(model=model_name)


@responses.activate
def test_chat_nubonyxia(api):
    prompt = "test_prompt"
    expected_response = {"response": "test_response"}

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json=expected_response,
        status=200,
    )

    result = api.ChatNubonyxia(prompt)
    assert result == expected_response
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.olympia.bhub.cloud/generate"
    assert responses.calls[0].response.status_code == 200


@responses.activate
def test_chat(api):
    prompt = "test_prompt"
    expected_response = {"response": "test_response"}

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json=expected_response,
        status=200,
    )

    result = api.Chat(prompt)
    assert result == expected_response
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.olympia.bhub.cloud/generate"
    assert responses.calls[0].response.status_code == 200


@responses.activate
def test_chat_nubonyxia_request_failure(api):
    prompt = "test_prompt"

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(requests.exceptions.RequestException):
        api.ChatNubonyxia(prompt)


@responses.activate
def test_chat_request_failure(api):
    prompt = "test_prompt"

    responses.add(
        responses.POST,
        "https://api.olympia.bhub.cloud/generate",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(requests.exceptions.RequestException):
        api.Chat(prompt)
