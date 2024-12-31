import pytest
from server import app
from interfaces import Question, Message
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
from analysis import (
    ask_question_with_history,
    ask_standalone_question,
    make_standalone_question_message,
    MODEL_TOKEN_LIMIT,
    ROLE,
    MODEL,
    API_ERROR_RESPONSE,
)


def test_standalone_question_message():
    question, transcript = "question", "transcript"
    # sanity check there is an actual prompt
    assert len(make_standalone_question_message(question, transcript)) > len(
        question + transcript
    )


# check if we correctly send a standalone question for a transcript
@pytest.mark.asyncio
async def test_ask_question_no_history():

    mock_count = AsyncMock()
    mock_count.status_code = 200

    mock_send = AsyncMock()
    mock_send.status_code = 200

    question_without_history = Question(question="question")

    with patch(
        "analysis.client.messages.count_tokens", mock_count
    ) as mock_count_tokens, patch(
        "analysis.client.messages.create", mock_send
    ) as mock_answer:

        mock_count_tokens.return_value = SimpleNamespace(
            **{"input_tokens": MODEL_TOKEN_LIMIT}
        )
        mock_answer.return_value = SimpleNamespace(
            **{"content": [SimpleNamespace(**{"text": "answer"})]}
        )

        transcript = "transcript"

        expected_initial_message = {
            "content": make_standalone_question_message(
                question_without_history.question, transcript
            ),
            "role": "user",
        }

        answer = await ask_standalone_question(question_without_history, transcript)
        mock_count_tokens.assert_awaited_once_with(
            model=MODEL,
            messages=[expected_initial_message],
            system=ROLE,
        )
        mock_answer.assert_awaited_once_with(
            model=MODEL,
            messages=[expected_initial_message],
            system=ROLE,
            temperature=0.0,
            max_tokens=MODEL_TOKEN_LIMIT,
        )
        assert answer == "answer"


# check if we propagate previous conversation history if such is provided
@pytest.mark.asyncio
async def test_ask_question_with_history():

    mock_count = AsyncMock()
    mock_count.status_code = 200

    mock_send = AsyncMock()
    mock_send.status_code = 200

    question_with_history = Question(
        question="question",
        conversation_history=[
            Message(content="previous_question"),
            Message(content="response_to_previous_question", role="assistant"),
        ],
    )

    with patch(
        "analysis.client.messages.count_tokens", mock_count
    ) as mock_count_tokens, patch(
        "analysis.client.messages.create", mock_send
    ) as mock_answer:

        mock_count_tokens.return_value = SimpleNamespace(
            **{"input_tokens": MODEL_TOKEN_LIMIT}
        )
        mock_answer.return_value = SimpleNamespace(
            **{"content": [SimpleNamespace(**{"text": "answer"})]}
        )

        expected_new_conversation_history = [
            *question_with_history.conversation_history,
            {"content": question_with_history.question, "role": "user"},
        ]

        answer = await ask_question_with_history(question_with_history)
        mock_count_tokens.assert_awaited_once_with(
            model=MODEL,
            messages=expected_new_conversation_history,
            system=ROLE,
        )
        mock_answer.assert_awaited_once_with(
            model=MODEL,
            messages=expected_new_conversation_history,
            system=ROLE,
            temperature=0.0,
            max_tokens=MODEL_TOKEN_LIMIT,
        )
        assert answer == "answer"


# check if we correctly handle error from anthropic api
@pytest.mark.asyncio
async def test_ask_question():

    mock_error = AsyncMock()
    mock_error.status_code = 400
    mock_error.side_effect = RuntimeError("something went wrong")

    question = Question(question="question", conversation_history=[])

    with patch("analysis.client.messages.count_tokens", mock_error):

        answer = await ask_standalone_question(question, "")
        assert answer == API_ERROR_RESPONSE

    with patch("analysis.client.messages.create", mock_error):

        answer = await ask_standalone_question(question, "")
        assert answer == API_ERROR_RESPONSE
