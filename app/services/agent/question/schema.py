from typing import Annotated, List, Union
from pydantic import Field
from app.services.agent.core.schema import AgentMessageEvent, AgentResultEvent
from app.services.question.types import QuestionUnion

class QuestionAgentResult(AgentResultEvent):
    data: List[QuestionUnion]
    
# 联合类型, 用于在StreamingResponse中使用
# OpenAPI看起来会通过Field的discriminator来判断是哪个类型, 并且自动Enum到对应的类型
QuestionAgentEventUnion = Annotated[
    Union[AgentMessageEvent, QuestionAgentResult],
    Field(discriminator="type"),
]