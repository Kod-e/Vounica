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
    user.hashed_password = "hashed_password"
    user.token_quota = 100000.0
    user.is_active = True
    return user


@pytest_asyncio.fixture(scope="function")
async def setup_user_data(async_db_session, test_user):
    """将测试用户添加到数据库"""
    async_db_session.add(test_user)
    await async_db_session.commit()
    return test_user


@pytest_asyncio.fixture(scope="function")
async def setup_vocab_data(async_db_session, test_user):
    """添加词汇数据"""
    vocab_data = [
        {"name": "こんにちは", "usage": "你好，日常问候语", "user_id": test_user.id},
        {"name": "ありがとう", "usage": "谢谢，表达感谢", "user_id": test_user.id},
        {"name": "すみません", "usage": "对不起/打扰了，表达歉意", "user_id": test_user.id},
        {"name": "はい", "usage": "是的，表示同意", "user_id": test_user.id},
        {"name": "いいえ", "usage": "不，表示否定", "user_id": test_user.id}
    ]
    
    vocabs = []
    for data in vocab_data:
        vocab = Vocab(**data)
        async_db_session.add(vocab)
        vocabs.append(vocab)
    
    await async_db_session.commit()
    return vocabs


@pytest_asyncio.fixture(scope="function")
async def setup_grammar_data(async_db_session, test_user):
    """添加语法数据"""
    grammar_data = [
        {"name": "です・ます形", "usage": "礼貌形式，用于正式场合", "user_id": test_user.id},
        {"name": "て形", "usage": "连接形式，表示动作的连续", "user_id": test_user.id},
        {"name": "た形", "usage": "过去时，表示已完成的动作", "user_id": test_user.id}
    ]
    
    grammars = []
    for data in grammar_data:
        grammar = Grammar(**data)
        async_db_session.add(grammar)
        grammars.append(grammar)
    
    await async_db_session.commit()
    return grammars


@pytest_asyncio.fixture(scope="function")
async def setup_memory_data(async_db_session, test_user):
    """添加记忆数据"""
    memory_data = [
        {"content": "用户喜欢动漫和日本文化", "category": "preference", "user_id": test_user.id},
        {"content": "用户学习日语的目标是能够看懂动漫", "category": "learning_goal", "user_id": test_user.id},
        {"content": "用户经常混淆「は」和「が」的用法", "category": "difficulty", "user_id": test_user.id},
        {"content": "用户正在学习N5水平的内容", "category": "level", "user_id": test_user.id},
        {"content": "用户希望重点学习日常会话", "category": "preference", "user_id": test_user.id}
    ]
    
    memories = []
    for data in memory_data:
        memory = Memory(**data)
        async_db_session.add(memory)
        memories.append(memory)
    
    await async_db_session.commit()
    return memories


@pytest_asyncio.fixture(scope="function")
async def setup_mistake_data(async_db_session, test_user):
    """添加错题数据"""
    mistake_data = [
        {
            "question": "如何说'你好'?",
            "question_type": "choice",
            "language_type": "ja",
            "answer": "おはよう",
            "correct_answer": "こんにちは",
            "error_reason": "混淆了'你好'和'早上好'的表达",
            "user_id": test_user.id
        },
        {
            "question": "请选择正确的句子：'我喜欢日本料理'",
            "question_type": "choice",
            "language_type": "ja",
            "answer": "私は日本料理好き",
            "correct_answer": "私は日本料理が好きです",
            "error_reason": "缺少助词'が'和礼貌形式'です'",
            "user_id": test_user.id
        }
    ]
    
    mistakes = []
    for data in mistake_data:
        mistake = Mistake(**data)
        async_db_session.add(mistake)
        mistakes.append(mistake)
    
    await async_db_session.commit()
    return mistakes


@pytest_asyncio.fixture(scope="function")
async def setup_story_data(async_db_session, test_user):
    """添加故事数据"""
    story_data = [
        {
            "content": "昨日、私は友達と一緒に映画館に行きました。とても面白い映画を見ました。",
            "summary": "用户记录的一篇关于去电影院的短文",
            "category": "日常生活",
            "user_id": test_user.id
        }
    ]
    
    stories = []
    for data in story_data:
        story = Story(**data)
        async_db_session.add(story)
        stories.append(story)
    
    await async_db_session.commit()
    return stories


@pytest_asyncio.fixture(scope="function")
async def test_uow(async_db_session, redis_client, mock_vector_session, test_user, 
                 setup_user_data, setup_vocab_data, setup_grammar_data, 
                 setup_memory_data, setup_mistake_data, setup_story_data):
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
        accept_language="zh-CN",
        target_language="ja",
        quota=quota_bucket
    )
    
    return uow


@pytest_asyncio.fixture(scope="function")
async def uow_with_custom_memories(async_db_session, redis_client, mock_vector_session, test_user):
    """创建带有自定义记忆的UoW工厂函数"""
    async def create_uow_with_memories(memories: List[Dict[str, Any]]) -> UnitOfWork:
        """
        创建一个带有指定记忆的UnitOfWork
        
        Args:
            memories: 自定义记忆列表，每个记忆是一个字典，包含content和category
        """
        # 清理现有记忆
        await async_db_session.execute(text("DELETE FROM memory WHERE user_id = :user_id"), 
                                      {"user_id": test_user.id})
        await async_db_session.commit()
        
        # 添加新的自定义记忆
        for memory_data in memories:
            memory = Memory(
                content=memory_data["content"],
                category=memory_data.get("category", "custom"),
                user_id=test_user.id
            )
            async_db_session.add(memory)
        
        await async_db_session.commit()
        
        # 创建配额桶
        quota_bucket = QuotaBucket(
            redis_client=redis_client,
            user=test_user,
            window=3600
        )
        
        # 构建UoW
        uow = UnitOfWork(
            db=async_db_session,
            vector=mock_vector_session,
            redis=redis_client,
            current_user=test_user,
            accept_language="zh-CN",
            target_language="ja",
            quota=quota_bucket
        )
        
        return uow
    
    return create_uow_with_memories


@pytest.fixture(scope="function")
def mock_chat_completion():
    """创建模拟的chat_completion函数"""
    class MockChoice:
        def __init__(self, content):
            self.message = MagicMock(content=content)
            
    class MockResponse:
        def __init__(self, content):
            self.choices = [MockChoice(content)]
            self.usage = MagicMock(total_tokens=100)
    
    async_mock = AsyncMock()
    
    # 默认响应
    response = MockResponse("这是一个模拟的LLM回复")
    async_mock.return_value = response
    
    return async_mock


@pytest.fixture(scope="function")
def mock_chat_completion_factory():
    """创建可配置的mock_chat_completion工厂"""
    def create_mock(responses=None, function_calls=None):
        """
        创建一个模拟的chat_completion函数
        
        Args:
            responses: 按顺序返回的响应内容列表
            function_calls: 按顺序返回的函数调用列表
        """
        responses = responses or ["这是一个模拟的LLM回复"]
        function_calls = function_calls or []
        call_count = 0
        
        class MockChoice:
            def __init__(self, content, function_call=None):
                self.message = MagicMock(content=content, function_call=function_call)
                
        class MockResponse:
            def __init__(self, content, function_call=None):
                self.choices = [MockChoice(content, function_call)]
                self.usage = MagicMock(total_tokens=100)
        
        async def mock_func(**kwargs):
            nonlocal call_count
            # 检查是否是函数调用
            if call_count < len(function_calls):
                fc = function_calls[call_count]
                response = MockResponse(
                    content=responses[min(call_count, len(responses)-1)],
                    function_call=MagicMock(name=fc["name"], arguments=json.dumps(fc["args"]))
                )
            else:
                response = MockResponse(
                    content=responses[min(call_count, len(responses)-1)]
                )
            
            call_count += 1
            return response
        
        return AsyncMock(side_effect=mock_func)
    
    return create_mock 