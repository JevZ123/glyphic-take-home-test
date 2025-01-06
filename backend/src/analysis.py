from typing import List

import anthropic

from interfaces import Message, Question

API_ERROR_RESPONSE = "No response"
TRANSCRIPT_PROMPT = """
I want you to answer questions based on a call transcript that I will provide.
The call transcript has each participant's (a.k.a. party's) utterances labelled in the form of '<time of utterance relative to call start> participant role (participant name): utterance'.

When answering the questions do not include the < or > symbol around the time indicator.

The transcript is as follows: '{transcript}'.
""".replace(
    "\n", ""
)

QUESTION_PROMPT = "{extra_context}{question}"

ROLE = "You are a sales call analysis expert"
MODEL = "claude-3-5-haiku-20241022"
MODEL_TOKEN_LIMIT = 8192

client = anthropic.AsyncAnthropic()


async def send_to_anthropic(
    new_message: Message, conversation_history: List[Message] = []
):

    conversation_history.append(new_message.model_dump())
    # NOTE: same use as for the sync API, but different client class
    # https://github.com/anthropics/anthropic-sdk-python?tab=readme-ov-file#async-usage

    print(f"sending messages:\n{conversation_history}")
    try:
        # use minimum amount of tokens possible
        tokens = min(
            MODEL_TOKEN_LIMIT,
            (
                await client.messages.count_tokens(
                    model=MODEL, messages=conversation_history, system=ROLE
                )
            ).input_tokens,
        )

        return (
            (
                await client.messages.create(
                    # limit spending
                    model=MODEL,
                    messages=conversation_history,
                    # give it a role
                    system=ROLE,
                    # most deterministic the model can provide
                    temperature=0.0,
                    max_tokens=tokens,
                )
            )
            .content[-1]
            .text
        )
    except Exception as e:
        print(e)
        return API_ERROR_RESPONSE


# standalone/initial message template
def make_standalone_question_message(question: str, transcript: str) -> str:
    return QUESTION_PROMPT.format(
        extra_context=TRANSCRIPT_PROMPT.format(transcript=transcript), question=question
    )


async def ask_question_with_history(question: Question):
    return await send_to_anthropic(
        Message(
            content=QUESTION_PROMPT.format(extra_context="", question=question.question)
        ),
        question.conversation_history,
    )


async def ask_standalone_question(question: Question, transcript: str):
    return await send_to_anthropic(
        Message(content=make_standalone_question_message(question.question, transcript))
    )
