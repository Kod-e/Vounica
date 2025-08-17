from fastapi import APIRouter, Depends, Body, Header, Request
from fastapi.responses import StreamingResponse
import asyncio, json, urllib.parse
from app.services.agent.question.agent import QuestionAgent
from app.services.question.types import QuestionUnion, QuestionListAdapter
from typing import List
from app.services.logic.question import QuestionHandler
from app.services.question.base.spec import JudgeResult
from app.services.agent.core.schema import AgentEventType
from app.services.agent.question.schema import QuestionAgentEvent
from app.infra.uow import get_uow
from app.services.agent.record.agent import RecordAgent
from app.services.agent.record.schema import RecordAgentEvent, RecordAgentRequestData
from fastapi import WebSocket, WebSocketDisconnect
from app.infra.uow import get_uow_ws
import contextlib   
router = APIRouter(prefix="/question", tags=["question"])


# StreamingResponse 流式返回 Agent 进度与结果
@router.post(
    "/agent/question/stream",
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
async def make_question_by_agent_stream(
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


@router.websocket("/agent/question/ws")
async def make_question_by_agent_ws(
    websocket: WebSocket,
    uow = Depends(get_uow_ws),
):
    await websocket.accept()
    question_agent = QuestionAgent()
    try:
        # 接收第一条包含 user_input 的消息，或从 query 参数读取
        user_input = websocket.query_params.get("user_input")
        if not user_input:
            msg = await websocket.receive_text()
            with contextlib.suppress(Exception):
                import json as _json
                obj = _json.loads(msg)
                if isinstance(obj, dict) and "user_input" in obj:
                    user_input = obj["user_input"]
                else:
                    user_input = msg
        async for ev in question_agent.run_stream(user_input):
            await websocket.send_text(ev.model_dump_json())
    except WebSocketDisconnect:
        pass
    finally:
        with contextlib.suppress(Exception):
            await websocket.close()

@router.post("/agent/question", response_model=List[QuestionUnion])
async def make_question_by_agent(
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
    data: RecordAgentRequestData = Body(...)
):
    question_handler = QuestionHandler()
    return await question_handler.record(data.questions)

# Stream记录用户的回答
@router.post("/agent/record/stream",    
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
    data: RecordAgentRequestData = Body(...)
):
    record_agent = RecordAgent()
    # 进行URL解码
    async def event_gen():
        async for ev in record_agent.run_stream(data.user_input, data.questions):
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


@router.websocket("/agent/record/ws")
async def record_question_ws(
    websocket: WebSocket,
    uow = Depends(get_uow_ws),
):
    await websocket.accept()
    record_agent = RecordAgent()
    try:
        # 接收第一条包含 questions 的消息
        msg = await websocket.receive_text()
        msg_dict = json.loads(msg)
        user_input = msg_dict["user_input"]
        questions: List[QuestionUnion] = QuestionListAdapter.validate_python(msg_dict["questions"])
        async for ev in record_agent.run_stream(user_input, questions):
            await websocket.send_text(ev.model_dump_json())
            if ev.type == AgentEventType.RESULT:
                break
    except WebSocketDisconnect:
        pass
    finally:
        with contextlib.suppress(Exception):
            await websocket.close()

# 获得错误原因
@router.post("/error_reason", response_model=JudgeResult)
async def get_error_reason(
    uow = Depends(get_uow),
    question: QuestionUnion = Body(...)
):
    question_handler = QuestionHandler()
    return await question_handler.judge(question)