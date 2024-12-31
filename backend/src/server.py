from typing import List
from enum import Enum
from contextlib import asynccontextmanager
import json

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from aiocache import SimpleMemoryCache
from aiocache.serializers import JsonSerializer

from interfaces import Question, CallRecordsList, CallRecord, CallMetadata
from analysis import ask_question_with_history, ask_standalone_question

CALLS_FILE_PATH = "calls.json"
CLIENT_SIDE_CACHE_EXPIRY_TIME = 60
SERVER_SIDE_CACHE_EXPIRY_TIME = 60


class CacheKey(Enum):
    IDS = "ids"
    METADATA = "metadata"
    TRANSCRIPT = "transcript"


def load_calls_from_file(file_path: str = CALLS_FILE_PATH) -> dict[str, CallRecord]:
    with open(file_path, "r") as file:
        return process_calls_json(json.load(file))


def process_calls_json(calls_json: List[dict]) -> dict[str, CallRecord]:
    result = {}
    for call in CallRecordsList(calls_json).root:
        # for ease of access via id later on
        call.call_metadata.call_id = call.id
        result[call.id] = call
    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = SimpleMemoryCache(
        serializer=JsonSerializer(), ttl=SERVER_SIDE_CACHE_EXPIRY_TIME
    )
    app.state.calls = load_calls_from_file()
    yield


app = FastAPI(root_path="/calls", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# get all the call IDs that the system has access to (NOTE: allows for auth extension)
@app.get("/ids", response_model=List[str])
async def call_ids():

    # NOTE: this cache is a placeholder, future implementation will store calls remotely (e.g., in a database or cloud storage)
    ids = await app.state.cache.get(CacheKey.IDS.value)

    if not ids:
        ids = list(app.state.calls.keys())
        await app.state.cache.set(CacheKey.IDS.value, ids)

    return JSONResponse(
        content=ids,
        headers={"Cache-Control": f"public, max-age={CLIENT_SIDE_CACHE_EXPIRY_TIME}"},
    )


# get all the metadata for display for a particular call
@app.get("/metadata/{call_id}", response_model=CallMetadata)
async def call_metadata(call_id: str):

    cache_key = f"{CacheKey.METADATA.value}-{call_id}"
    # NOTE: this cache is a placeholder, future implementation will store calls remotely (e.g., in a database or cloud storage)
    metadata = await app.state.cache.get(cache_key)

    if not metadata:
        if not call_id in app.state.calls:
            raise HTTPException(status_code=404, detail=f"No call id {call_id} found")

        metadata = app.state.calls[call_id].call_metadata
        metadata = jsonable_encoder(metadata)
        await app.state.cache.set(cache_key, metadata)

    return JSONResponse(
        content=metadata,
        headers={"Cache-Control": f"public, max-age={CLIENT_SIDE_CACHE_EXPIRY_TIME}"},
    )


@app.post("/ask-question/{call_id}", response_model=str)
async def ask(call_id: str, question: Question):

    if question.conversation_history:
        answer = await ask_question_with_history(question)
    else:
        transcript_cache_key = f"{CacheKey.TRANSCRIPT.value}-{call_id}"

        # NOTE: this cache is a placeholder, future implementation will store calls remotely (e.g., in a database or cloud storage)
        transcript = await app.state.cache.get(transcript_cache_key)

        if not transcript:

            if not call_id in app.state.calls:
                raise HTTPException(
                    status_code=404, detail=f"No call id {call_id} found"
                )

            transcript = app.state.calls[call_id].transcript.text
            await app.state.cache.set(transcript_cache_key, transcript)

        answer = await ask_standalone_question(question, transcript)

    return JSONResponse(
        content=answer,
        headers={"Cache-Control": f"public, max-age={CLIENT_SIDE_CACHE_EXPIRY_TIME}"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
