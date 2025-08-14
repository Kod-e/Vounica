from typing import Annotated, List, Union
from pydantic import Field, RootModel
from app.services.agent.core.schema import AgentResultEvent,AgentThinkingEvent,AgentMessageEvent,AgentStreamChunkEvent,AgentStreamEndEvent,AgentToolCallEvent
from app.services.question.types import QuestionUnion

class QuestionAgentResult(AgentResultEvent):
    data: List[QuestionUnion]
    
# 联合类型, 用于在StreamingResponse中使用
# OpenAPI看起来会通过Field的discriminator来判断是哪个类型, 并且自动Enum到对应的类型
QuestionAgentEventUnion = Annotated[
    Union[AgentMessageEvent, QuestionAgentResult, AgentThinkingEvent, AgentStreamChunkEvent, AgentStreamEndEvent, AgentToolCallEvent],
    Field(discriminator="type"),
]
class QuestionAgentEvent(RootModel[QuestionAgentEventUnion]):
    pass