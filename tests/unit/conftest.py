"""
Unit testing fixtures for app.

These fixtures provide an easy way to set up test users, mock database connections,
and other components needed for unit testing.

Unlike integration tests, these fixtures focus on mocking dependencies rather than
using real external services.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock

from app.infra.models.user import User
from app.infra.uow import UnitOfWork
from app.core.vector.session import VectorSession


@pytest.fixture
def mock_db_session():
    """
    Create a mock SQLAlchemy session.
    
    mockされたSQLAlchemy sessionを提供(ていきょう)します。
    実際(じっさい)のデータベースには接続(せつぞく)しません。
    """
    mock_session = MagicMock()
    
    # Add mock query functionality
    mock_query = MagicMock()
    mock_session.query = MagicMock(return_value=mock_query)
    mock_query.filter = MagicMock(return_value=mock_query)
    mock_query.first = MagicMock(return_value=None)
    
    # Mock async methods
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    
    return mock_session


@pytest.fixture
def mock_vector_session():
    """
    Create a mock vector database session.
    
    mockされたvector database sessionを提供(ていきょう)します。
    実際(じっさい)のQdrantには接続(せつぞく)しません。
    """
    mock_vector = MagicMock(spec=VectorSession)
    mock_vector.client = MagicMock()
    mock_vector.search = AsyncMock(return_value=[])
    
    return mock_vector


@pytest.fixture
def mock_redis_client():
    """
    Create a mock Redis client.
    
    mockされたRedis clientを提供(ていきょう)します。
    実際(じっさい)のRedisには接続(せつぞく)しません。
    """
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    
    return mock_redis


@pytest.fixture
def test_user():
    """
    Create a test user model instance.
    
    テスト用(よう)のユーザーモデルインスタンスを提供(ていきょう)します。
    """
    user = User()
    user.id = 1
    user.name = "Test User"
    user.email = "test@example.com"
    user.hashed_password = "hashed_password"
    user.is_active = True
    
    return user


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """
    Test user data dictionary.
    
    テスト用(よう)のユーザーデータ辞書(じしょ)を提供(ていきょう)します。
    """
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }


@pytest.fixture
def mock_uow(mock_db_session, mock_vector_session, mock_redis_client, test_user):
    """
    Create a mock Unit of Work with all necessary components.
    
    すべての必要(ひつよう)なコンポーネントを持つmock UoWを提供(ていきょう)します。
    """
    uow = UnitOfWork(
        db=mock_db_session,
        vector=mock_vector_session,
        redis=mock_redis_client,
        current_user=test_user,
        accept_language="en",
        target_language="ja"
    )
    
    return uow


@pytest.fixture
def new_user_uow(mock_db_session, mock_vector_session, mock_redis_client):
    """
    Create a UoW for a new user without history.
    
    履歴(りれき)のない新(あたら)しいユーザーのためのUoWを提供(ていきょう)します。
    """
    new_user = User()
    new_user.id = 2
    new_user.name = "New User"
    new_user.email = "new@example.com"
    new_user.is_active = True
    
    uow = UnitOfWork(
        db=mock_db_session,
        vector=mock_vector_session,
        redis=mock_redis_client,
        current_user=new_user,
        accept_language="en",
        target_language="ja"
    )
    
    return uow


@pytest.fixture
def advanced_user_uow(mock_db_session, mock_vector_session, mock_redis_client):
    """
    Create a UoW for an advanced user.
    
    上級(じょうきゅう)ユーザーのためのUoWを提供(ていきょう)します。
    """
    advanced_user = User()
    advanced_user.id = 3
    advanced_user.name = "Advanced User"
    advanced_user.email = "advanced@example.com"
    advanced_user.is_active = True
    
    uow = UnitOfWork(
        db=mock_db_session,
        vector=mock_vector_session,
        redis=mock_redis_client,
        current_user=advanced_user,
        accept_language="en",
        target_language="ja"
    )
    
    return uow


@pytest.fixture
def mock_search_resource():
    """
    Mock the search_resource function.
    
    search_resource 関数(かんすう)をmockします。
    """
    async def mock_search(*args, **kwargs):
        # Default empty search results
        return []
    
    return AsyncMock(side_effect=mock_search)


@pytest.fixture
def mock_chat_completion():
    """
    Mock the chat_completion function.
    
    chat_completion 関数(かんすう)をmockします。
    """
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Mocked LLM response"
            )
        )
    ]
    
    return MagicMock(return_value=mock_response) 