from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional

from app.core.db import get_db

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