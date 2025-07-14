from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime
from typing import AsyncGenerator
# 为了避免在模块导入阶段固定 async_session_maker 的引用，
# 避免出现 FastAPI lifespan 更新后 core 内仍然是 None 的问题，
# 这里通过 importlib 在每次 get_db 调用时按需获取最新的
# async_session_maker，保证依赖注入正常。
from sqlalchemy.ext.asyncio import AsyncSession
import importlib

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
    
    
# DB セッション依存関数
# この関数は FastAPI の Depends で注入されます。
# 每次调用时动态获取 app.main.async_session_maker，保证其已在 lifespan 中初始化。

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for each request
    Use async context manager to ensure session is properly released
    """
    main_module = importlib.import_module("app.main")
    session_maker = getattr(main_module, "async_session_maker", None)

    if session_maker is None:
        raise RuntimeError("DB Session Maker is not initialized")

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise