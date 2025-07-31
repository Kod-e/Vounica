from fastapi import APIRouter
from app.services.agent.question.agent import QuestionAgent
from app.services.question.types import QuestionUnion, QuestionAdapter
from typing import List
router = APIRouter(prefix="/question", tags=["question"])

@router.post("/agent/chat", response_model=List[QuestionUnion])
async def make_question_by_chat(user_input: str):
    question_agent = QuestionAgent()
    await question_agent.run(user_input)
    return QuestionAdapter.validate_python(question_agent.question_stack.questions)