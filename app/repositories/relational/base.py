from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import async_session_maker

Base = declarative_base()

# 增加基础的表, 定义created_at和updated_at
class BaseModel(Base):
    """
    The base model for all tables.
    これはすべてのTableのBaseModelです。
    created_at: 作成日時
    updated_at: 更新日時
    """
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    
# 依赖项，用于获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for each request
    Use async context manager to ensure session is properly released
    """
    if async_session_maker is None:
        raise RuntimeError("数据库会话工厂未初始化")
        
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise