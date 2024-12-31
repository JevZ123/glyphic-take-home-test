import pytest
from fastapi import status
from fastapi.testclient import TestClient
from server import app, process_calls_json
from interfaces import Question, CallMetadata, CallRecord, Message
from unittest.mock import AsyncMock, patch

SAMPLE_CALL = {
    "id": "id",
    "created_at_utc": "2077-01-01T00:01:00.0Z",
    "call_metadata": {
        "title": "title",
        "duration": 60,
        "start_time": "2077-01-01T00:00:00.0Z",
        "parties": [
            {
                "name": "name",
                "email": "someone@somewhere.com",
                "profile": {
                    "job_title": "someone",
                    "location": "somwhere",
                    "photo_url": "https://somwhere.com/some-photo",
                    "linkedin_url": "https://somwhere.com/some-profile",
                },
            }
        ],
    },
    "transcript": {"text": "text"},
    "inference_results": {"call_summary": "summary"},
}

SAMPLE_CALL_RECORD = CallRecord.model_validate(SAMPLE_CALL)
SAMPLE_CALLS = {SAMPLE_CALL_RECORD.id: SAMPLE_CALL_RECORD}


@pytest.fixture(scope="session", autouse=True)
def setup_once_for_all_tests():
    # done on call ingestion by the app, simulate it here
    SAMPLE_CALL_RECORD.call_metadata.call_id = SAMPLE_CALL_RECORD.id


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# basic test to see if we read in the records correctly
def test_call_json_processing():
    assert SAMPLE_CALLS == process_calls_json([SAMPLE_CALL])


# check if the ids endpoint works correctly
def test_call_ids(client):
    app.state.calls = SAMPLE_CALLS

    response = client.get("/calls/ids")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == list(SAMPLE_CALLS.keys())


# check if the metadata endpoint is valid
def test_call_metadata(client):
    app.state.calls = SAMPLE_CALLS

    response = client.get(f"/calls/metadata/{SAMPLE_CALL_RECORD.id}")

    assert response.status_code == status.HTTP_200_OK
    assert (
        CallMetadata.model_validate(response.json()) == SAMPLE_CALL_RECORD.call_metadata
    )


# check if 404 works correctly on metadata endpoint
def test_call_metadata_nonexistent_id(client):
    app.state.calls = SAMPLE_CALLS

    response = client.get("/metadata/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# check if the question endpoint is valid for standalone questions
def test_ask_standalone_question(client):
    app.state.calls = SAMPLE_CALLS
    mock = AsyncMock()
    with patch("server.ask_standalone_question", mock) as mock_question:
        mock_question.return_value = "answer"

        question = Question(question="")
        response = client.post(
            f"/calls/ask-question/{SAMPLE_CALL_RECORD.id}",
            json=question.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == "answer"

        mock_question.assert_awaited_with(question, SAMPLE_CALL_RECORD.transcript.text)


# check if the question endpoint is valid for questions with a conversation history
def test_ask_question_with_history(client):
    app.state.calls = SAMPLE_CALLS

    mock = AsyncMock()
    with patch("server.ask_question_with_history", mock) as mock_question:
        mock_question.return_value = "answer"

        message = Message(content="")
        question = Question(question="", conversation_history=[message])
        response = client.post(
            f"/calls/ask-question/{SAMPLE_CALL_RECORD.id}",
            json=question.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == "answer"

        mock_question.assert_awaited_with(question)


# check if asking about a nonexistant call fails correctly
def test_ask_invalid_question(client):

    question = Question(question="")
    response = client.post(
        f"/calls/ask-question/nonexistant-id", json=question.model_dump()
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
