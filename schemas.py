# Python import 
from typing import Any, List, Optional, Literal, Dict
from uuid import uuid4

# Library import 
from pydantic import BaseModel, Field

# Module import 


class MessagePart(BaseModel):
    kind: Literal["text", "data"]
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class A2AMessage(BaseModel):
    kind: Literal["message"] = "message"
    role: Literal["user", "agent", "system"]
    parts: List[MessagePart]
    messageId: str = Field(default_factory=lambda: str(uuid4()))
    taskId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PhraseSchema(BaseModel):
    sentence: str


class GrammarResponse(BaseModel):
    correction: str
    explanation: str
