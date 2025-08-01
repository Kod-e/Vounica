from typing import List
from app.services.agent.core.schema import AgentResultEvent
from app.services.question.types import QuestionUnion

class QuestionAgentResult(AgentResultEvent):
    data: List[QuestionUnion]