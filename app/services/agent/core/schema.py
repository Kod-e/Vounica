from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal

class AgentEventType(str, Enum):
    MESSAGE = "message"
    RESULT = "result"

    THINKING = "thinking"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"

    TOOL_CALL = "tool_call"
    


class AgentEvent(BaseModel):
    type: AgentEventType
    data: BaseModel

class AgentMessageData(BaseModel):
    emoji: str
    message: str
    
class AgentToolData(BaseModel):
    tool_name: str
    tool_input: str

class AgentStreamChunkData(BaseModel):
    chunk: str
    
class AgentThinkingData(BaseModel):
    pass
class AgentStreamEndData(BaseModel):
    pass

class AgentThinkingEvent(AgentEvent):
    type: Literal[AgentEventType.THINKING] = Field(default=AgentEventType.THINKING)
    data: AgentThinkingData = Field(default_factory=AgentThinkingData)

class AgentStreamChunkEvent(AgentEvent):
    type: Literal[AgentEventType.STREAM_CHUNK] = Field(default=AgentEventType.STREAM_CHUNK)
    data: AgentStreamChunkData = Field(default_factory=AgentStreamChunkData)

class AgentStreamEndEvent(AgentEvent):
    type: Literal[AgentEventType.STREAM_END] = Field(default=AgentEventType.STREAM_END)
    data: AgentStreamEndData = Field(default_factory=AgentStreamEndData)

class AgentToolCallEvent(AgentEvent):
    type: Literal[AgentEventType.TOOL_CALL] = Field(default=AgentEventType.TOOL_CALL)
    data: AgentToolData = Field(default_factory=AgentToolData)

class AgentMessageEvent(AgentEvent):
    type: Literal[AgentEventType.MESSAGE] = Field(default=AgentEventType.MESSAGE)
    data: AgentMessageData

class AgentResultEvent(AgentEvent):
    type: Literal[AgentEventType.RESULT] = Field(default=AgentEventType.RESULT)
    data: BaseModel