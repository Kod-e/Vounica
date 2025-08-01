from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio, json
from app.services.agent.question.agent import QuestionAgent
from app.services.question.types import QuestionUnion, QuestionAdapter
from typing import List
from app.services.logic.question import QuestionHandler
from app.services.question.base.spec import JudgeResult
from app.infra.context import uow_ctx

router = APIRouter(prefix="/question", tags=["question"])


# StreamingResponse 流式返回 Agent 进度与结果
@router.post("/agent/chat/stream")
async def make_question_by_chat_stream(user_input: str):
    """即时流式返回 Agent 进度与结果 (SSE)。"""

    question_agent = QuestionAgent()
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(question_agent.run_stream(user_input), media_type="text/agent-event-stream", headers=headers)

@router.post("/agent/chat", response_model=List[QuestionUnion])
async def make_question_by_chat(user_input: str):
    question_agent = QuestionAgent()
    return await question_agent.run(user_input)

@router.post("/judge" , response_model=JudgeResult)
async def judge_question(question: QuestionUnion):
    question_handler = QuestionHandler()
    return await question_handler.judge(question)