from typing import Annotated, List, Union
from pydantic import Field, RootModel, BaseModel
from app.services.agent.core.schema import AgentResultEvent,AgentThinkingEvent,AgentMessageEvent,AgentStreamChunkEvent,AgentStreamEndEvent,AgentToolCallEvent
from app.services.question.base.spec import JudgeResult

class RecordAgentResultData(BaseModel):
    judge_results: List[JudgeResult]
    suggestion: str
    
class RecordAgentResultEvent(AgentResultEvent):
    data: RecordAgentResultData

# 联合类型, 用于在StreamingResponse中使用
# OpenAPI看起来会通过Field的discriminator来判断是哪个类型, 并且自动Enum到对应的类型
RecordAgentEventUnion = Annotated[
    Union[AgentMessageEvent, RecordAgentResultEvent, AgentThinkingEvent, AgentStreamChunkEvent, AgentStreamEndEvent, AgentToolCallEvent],
    Field(discriminator="type"),
]
class RecordAgentEvent(RootModel[RecordAgentEventUnion]):
    pass