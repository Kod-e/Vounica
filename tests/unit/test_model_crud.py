# 单元测试 - 模型CRUD操作
# 验证各个CRUD端点的实现
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime,timezone

# 导入我们要测试的视图函数
from app.api.v1.endpoints.grammar import create_grammar, update_grammar, delete_grammar, get_grammars
from app.api.v1.endpoints.mistake import create_mistake, update_mistake, delete_mistake, get_mistakes
from app.api.v1.endpoints.story import create_story, update_story, delete_story, get_stories
from app.api.v1.endpoints.vocab import create_vocab, update_vocab, delete_vocab, get_vocabs

# 导入Pydantic模型
from app.infra.schemas import (
    GrammarSchema, GrammarCreateSchema,
    MistakeSchema, MistakeCreateSchema,
    StorySchema, StoryCreateSchema,
    VocabSchema, VocabCreateSchema
)

# 准备测试数据
@pytest.fixture
def grammar_create_data():
    return GrammarCreateSchema(
        name="test grammar",
        usage="test usage",
        status=0.75,
        language="ja"
    )

@pytest.fixture
def mistake_create_data():
    return MistakeCreateSchema(
        question="test question",
        question_type="test_type",
        language="ja",
        answer="wrong answer",
        correct_answer="right answer",
        error_reason="explanation of error"
    )

@pytest.fixture
def story_create_data():
    return StoryCreateSchema(
        content="test content",
        summary="test summary",
        category="test category",
        language="ja"
    )

@pytest.fixture
def vocab_create_data():
    return VocabCreateSchema(
        name="test vocab",
        usage="test usage",
        status=0.6,
        language="ja"
    )

# 模拟数据库模型实例
@pytest.fixture
def mock_db_model():
    model = MagicMock()
    model.id = 1
    model.name = "test name"
    model.usage = "test usage"
    model.status = 0.8
    model.language = "ja"
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    # 为各种类型的模型添加特定属性
    model.content = "test content"
    model.summary = "test summary"
    model.category = "test category"
    model.question = "test question"
    model.question_type = "test_type"
    model.answer = "wrong answer"
    model.correct_answer = "right answer"
    model.error_reason = "explanation of error"
    return model

# Grammar 测试
@pytest.mark.asyncio
async def test_create_grammar(grammar_create_data, mock_db_model):
    # 准备
    service_mock = AsyncMock()
    service_mock.create.return_value = mock_db_model
    
    # 执行
    result = await create_grammar(MagicMock(), service_mock, grammar_create_data)
    
    # 验证
    service_mock.create.assert_called_once()
    assert result is not None
    assert isinstance(result, GrammarSchema)

@pytest.mark.asyncio
async def test_update_grammar(mock_db_model):
    # 准备
    grammar_schema = GrammarSchema(
        id=1,
        name="test grammar",
        usage="test usage",
        status=0.75,
        language="ja",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    service_mock = AsyncMock()
    service_mock.update.return_value = mock_db_model
    
    # 执行
    result = await update_grammar(MagicMock(), service_mock, grammar_schema)
    
    # 验证
    service_mock.update.assert_called_once()
    assert result is not None
    assert isinstance(result, GrammarSchema)

@pytest.mark.asyncio
async def test_delete_grammar(mock_db_model):
    # 准备
    service_mock = AsyncMock()
    service_mock.delete.return_value = mock_db_model
    
    # 执行
    result = await delete_grammar(MagicMock(), service_mock, 1)
    
    # 验证
    service_mock.delete.assert_called_once_with(1)
    assert result is not None
    assert isinstance(result, GrammarSchema)

@pytest.mark.asyncio
async def test_get_grammars(mock_db_model):
    # 准备
    service_mock = AsyncMock()
    service_mock.list.return_value = [mock_db_model, mock_db_model]
    
    # 执行
    result = await get_grammars(MagicMock(), service_mock)
    
    # 验证
    service_mock.list.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, GrammarSchema) for item in result)

# Mistake 测试
@pytest.mark.asyncio
async def test_create_mistake(mistake_create_data, mock_db_model):
    service_mock = AsyncMock()
    service_mock.create.return_value = mock_db_model
    result = await create_mistake(MagicMock(), service_mock, mistake_create_data)
    service_mock.create.assert_called_once()
    assert result is not None
    assert isinstance(result, MistakeSchema)

# Story 测试
@pytest.mark.asyncio
async def test_create_story(story_create_data, mock_db_model):
    service_mock = AsyncMock()
    service_mock.create.return_value = mock_db_model
    result = await create_story(MagicMock(), service_mock, story_create_data)
    service_mock.create.assert_called_once()
    assert result is not None
    assert isinstance(result, StorySchema)

# Vocab 测试
@pytest.mark.asyncio
async def test_create_vocab(vocab_create_data, mock_db_model):
    service_mock = AsyncMock()
    service_mock.create.return_value = mock_db_model
    result = await create_vocab(MagicMock(), service_mock, vocab_create_data)
    service_mock.create.assert_called_once()
    assert result is not None
    assert isinstance(result, VocabSchema) 