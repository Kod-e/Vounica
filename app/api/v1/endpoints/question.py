from fastapi import APIRouter, Depends
from app.services.agent.question.agent import QuestionAgent
from app.services.question.types import QuestionUnion, QuestionAdapter
from typing import List
from app.services.logic.question import QuestionHandler
from app.services.question.base.spec import JudgeResult
from app.infra.context import uow_ctx

router = APIRouter(prefix="/question", tags=["question"])

@router.post("/agent/chat", response_model=List[QuestionUnion])
async def make_question_by_chat(user_input: str):
    question_agent = QuestionAgent()
    await question_agent.run(user_input)
    return QuestionAdapter.validate_python(question_agent.question_stack.questions)


@router.post("/judge" , response_model=JudgeResult)
async def judge_question(question: QuestionUnion):
    question_handler = QuestionHandler()
    return await question_handler.judge(question)