from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from app.core.db import get_db
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.memory import router as memory_router
from app.api.v1.endpoints.grammar import router as grammar_router
from app.api.v1.endpoints.mistake import router as mistake_router
from app.api.v1.endpoints.story import router as story_router
from app.api.v1.endpoints.vocab import router as vocab_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.question import router as question_router
# 创建路由实例
router = APIRouter(tags=["v1"])

# Health check endpoint
@router.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "ok", "version": "v1"}

# Database test endpoint
@router.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    """
    Test database connection endpoint
    """
    try:
        # 使用 text() 执行一个简单的SQL查询验证连接是否正常
        result = await db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        if row:
            return {"status": "database connection successful", "result": row[0]}
        return {"status": "database connection successful", "result": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# 注册所有路由
router.include_router(auth_router)
router.include_router(memory_router)
router.include_router(grammar_router)
router.include_router(mistake_router)
router.include_router(story_router)
router.include_router(vocab_router)
router.include_router(user_router)
router.include_router(question_router)