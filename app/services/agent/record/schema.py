from typing import Annotated, List, Union
from pydantic import Field, RootModel
from app.services.agent.core.schema import AgentResultEvent,AgentThinkingEvent,AgentMessageEvent,AgentStreamChunkEvent,AgentStreamEndEvent,AgentToolCallEvent
from app.services.question.base.spec import JudgeResult

class RecordAgentResult(AgentResultEvent):
    data: List[JudgeResult]

# 联合类型, 用于在StreamingResponse中使用
# OpenAPI看起来会通过Field的discriminator来判断是哪个类型, 并且自动Enum到对应的类型
RecordAgentEventUnion = Annotated[
    Union[AgentMessageEvent, RecordAgentResult, AgentThinkingEvent, AgentStreamChunkEvent, AgentStreamEndEvent, AgentToolCallEvent],
    Field(discriminator="type"),
]
class RecordAgentEvent(RootModel[RecordAgentEventUnion]):
    pass