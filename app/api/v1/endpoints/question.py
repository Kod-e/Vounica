from fastapi import APIRouter, Depends, Body, Header, Request
from fastapi.responses import StreamingResponse
import asyncio, json, urllib.parse
from app.services.agent.question.agent import QuestionAgent
from app.services.question.types import QuestionUnion, QuestionAdapter
from typing import List
from app.services.logic.question import QuestionHandler
from app.services.question.base.spec import JudgeResult
from app.services.agent.core.schema import AgentEvent, AgentMessageEvent
from app.services.agent.question.schema import QuestionAgentEvent
from app.infra.uow import get_uow
from app.services.agent.record.agent import RecordAgent
from app.services.agent.record.schema import RecordAgentEvent
router = APIRouter(prefix="/question", tags=["question"])


# StreamingResponse 流式返回 Agent 进度与结果
@router.post(
    "/agent/chat/stream",
    response_model=QuestionAgentEvent,   # 让它进入 components.schemas
    responses={
        200: {
            "description": "SSE stream; each 'data:' line is one JSON QuestionAgentEvent",
            "content": {
                "text/event-stream": {
                    # 添加Json路径
                    "schema": {"$ref": "#/components/schemas/QuestionAgentEvent"}
                }
            }
        }
    }
)
async def make_question_by_chat_stream(
    uow = Depends(get_uow),
    user_input: str = Body(...),
):
    """即时流式返回 Agent 进度与结果 (SSE)。"""
    question_agent = QuestionAgent()
    # 进行URL解码
    user_input = urllib.parse.unquote(user_input)
    async def event_gen():
        async for ev in question_agent.run_stream(user_input):
            result = "data: " + ev.model_dump_json() + "\n\n"
            # SSE 帧必须以 \n\n 结束；加 data: 兼容浏览器
            yield result

    return StreamingResponse(
        event_gen(),                      # ← 传包装后的 async-generator
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/agent/chat", response_model=List[QuestionUnion])
async def make_question_by_chat(
    uow = Depends(get_uow),
    user_input: str = Body(...)
):
    question_agent = QuestionAgent()
    return await question_agent.run(user_input)

@router.post("/judge" , response_model=JudgeResult)
async def judge_question(
    uow = Depends(get_uow),
    question: QuestionUnion = Body(...)
):
    question_handler = QuestionHandler()
    return await question_handler.judge(question)

# 记录用户的回答
@router.post("/record", response_model=List[JudgeResult])
async def record_question(
    uow = Depends(get_uow),
    questions: List[QuestionUnion] = Body(...)
):
    question_handler = QuestionHandler()
    return await question_handler.record(questions)

# Stream记录用户的回答
@router.post("/record/stream",    
    response_model=RecordAgentEvent,   # 让它进入 components.schemas
    responses={
        200: {
            "description": "SSE stream; each 'data:' line is one JSON RecordAgentEvent",
            "content": {
                "text/event-stream": {
                    # 添加Json路径
                    "schema": {"$ref": "#/components/schemas/RecordAgentEvent"}
                }
            }
        }
    }
)
async def record_question_by_stream(
    uow = Depends(get_uow),
    questions: List[QuestionUnion] = Body(...)
):
    record_agent = RecordAgent()
    # 进行URL解码
    async def event_gen():
        async for ev in record_agent.run_stream(questions):
            result = "data: " + ev.model_dump_json() + "\n\n"
            # SSE 帧必须以 \n\n 结束；加 data: 兼容浏览器
            yield result

    return StreamingResponse(
        event_gen(),                      # ← 传包装后的 async-generator
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

# 获得错误原因
@router.post("/error_reason", response_model=JudgeResult)
async def get_error_reason(
    uow = Depends(get_uow),
    question: QuestionUnion = Body(...)
):
    question_handler = QuestionHandler()
    return await question_handler.judge(question)