from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal

class AgentEventType(str, Enum):
    MESSAGE = "message"
    RESULT = "result"

class AgentEvent(BaseModel):
    type: AgentEventType
    data: BaseModel

class AgentMessageData(BaseModel):
    emoji: str
    message: str

class AgentMessageEvent(AgentEvent):
    type: Literal[AgentEventType.MESSAGE] = Field(default=AgentEventType.MESSAGE)
    data: AgentMessageData

class AgentResultEvent(AgentEvent):
    type: Literal[AgentEventType.RESULT] = Field(default=AgentEventType.RESULT)
    data: BaseModel