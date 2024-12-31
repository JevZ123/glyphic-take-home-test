from pydantic import BaseModel, EmailStr, RootModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Profile(BaseModel):
    job_title: str
    location: str
    photo_url: HttpUrl
    linkedin_url: HttpUrl


class Party(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    profile: Optional[Profile] = None


class CallMetadata(BaseModel):
    call_id: Optional[str] = None
    title: str
    duration: int
    start_time: datetime
    parties: List[Party]


class Transcript(BaseModel):
    text: str


class CallRecord(BaseModel):
    id: str
    created_at_utc: datetime
    call_metadata: CallMetadata
    transcript: Transcript


class CallRecordsList(RootModel):
    root: List[CallRecord]


class Message(BaseModel):
    content: str
    role: str = "user"


class Question(BaseModel):
    question: str
    conversation_history: List[Message] = []
