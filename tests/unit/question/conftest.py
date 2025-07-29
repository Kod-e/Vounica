"""
为QuestionAgent测试提供固定环境的fixture模块。

这个模块提供了在测试中使用的所有fixture，包括：
- SQLite内存数据库
- 内存Redis客户端
- 模拟向量数据库
- 预设用户数据和记忆
"""

import asyncio
import json
import pytest
import pytest_asyncio
import sqlite3
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List, Optional, Callable, Awaitable

import fakeredis.aioredis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.infra.models.user import User
from app.infra.models.vocab import Vocab
from app.infra.models.memory import Memory
from app.infra.models.mistake import Mistake
from app.infra.models.grammar import Grammar
from app.infra.models.story import Story
from app.infra.uow import UnitOfWork
from app.infra.quota.bucket import QuotaBucket
from app.core.db.base import Base
from app.core.vector.session import VectorSession
from app.llm.models import LLMModel

# 用于存储所有内存数据的全局变量
MEMORY_STORAGE = {}
VOCAB_STORAGE = {}
GRAMMAR_STORAGE = {}
STORY_STORAGE = {}
MISTAKE_STORAGE = {}


# 数据库配置
@pytest.fixture(scope="function")
def sqlite_engine():
    """创建SQLite内存数据库引擎"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest_asyncio.fixture(scope="function")
async def async_sqlite_engine():
    """创建异步SQLite内存数据库引擎"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def db_session(sqlite_engine):
    """创建同步数据库会话"""
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    yield session
    session.close()


@pytest_asyncio.fixture(scope="function")
async def async_db_session(async_sqlite_engine):
    """创建异步数据库会话"""
    async_session = async_sessionmaker(async_sqlite_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    """创建内存Redis客户端"""
    client = fakeredis.aioredis.FakeRedis()
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture(scope="function")
def mock_vector_session():
    """创建模拟向量数据库会话"""
    mock_session = MagicMock(spec=VectorSession)
    
    async def mock_search(collection_name, query_vector, limit=10, query_filter=None):
        """模拟向量搜索功能，根据集合名称返回不同结果"""
        # 模拟payload结构
        class MockPoint:
            def __init__(self, id, payload):
                self.id = id
                self.payload = payload
        
        if "vocab" in collection_name:
            return [MockPoint(i, {"origin_id": i, "text": f"vocab_{i}"}) for i in range(1, limit+1)]
        elif "grammar" in collection_name:
            return [MockPoint(i, {"origin_id": i, "text": f"grammar_{i}"}) for i in range(1, limit+1)]
        elif "memory" in collection_name:
            return [MockPoint(i, {"origin_id": i, "text": f"memory_{i}"}) for i in range(1, limit+1)]
        elif "story" in collection_name:
            return [MockPoint(i, {"origin_id": i, "text": f"story_{i}"}) for i in range(1, limit+1)]
        elif "mistake" in collection_name:
            return [MockPoint(i, {"origin_id": i, "text": f"mistake_{i}"}) for i in range(1, limit+1)]
        return []
    
    mock_session.search = AsyncMock(side_effect=mock_search)
    return mock_session


@pytest.fixture(scope="function")
def test_user():
    """创建测试用户"""
    user = User()
    user.id = 1
    user.name = "Test User"
    user.email = "test@example.com"
    user.password = "hashed_password"
    user.token_quota = 100000.0
    return user


@pytest_asyncio.fixture(scope="function")
async def setup_user_data(async_db_session, test_user):
    """将测试用户添加到数据库"""
    async_db_session.add(test_user)
    await async_db_session.commit()
    return test_user


@pytest_asyncio.fixture(scope="function")
async def test_uow(async_db_session, redis_client, mock_vector_session, test_user):
    """创建完整的测试UnitOfWork"""
    # 创建配额桶
    quota_bucket = QuotaBucket(
        redis_client=redis_client,
        user=test_user,
        window=3600  # 1小时窗口期
    )
    
    # 构建UoW
    uow = UnitOfWork(
        db=async_db_session,
        vector=mock_vector_session,
        redis=redis_client,
        current_user=test_user,
        current_user_id=test_user.id,
        accept_language="zh",
        target_language="ja",
        quota=quota_bucket
    )
    
    return uow