from pydantic import BaseModel
from enum import Enum
from typing import Any, Dict

class AgentEventType(str, Enum):
    MESSAGE = "message"
    RESULT = "result"
    

class AgentEvent(BaseModel):
    type: AgentEventType
    data: BaseModel

class AgentMessageData(BaseModel):
    emoji: str
    message: str

class AgentMessage(AgentEvent):
    type: AgentEventType = AgentEventType.MESSAGE
    data: AgentMessageData

class AgentResult(AgentEvent):
    type: AgentEventType = AgentEventType.RESULT
    data: BaseModel