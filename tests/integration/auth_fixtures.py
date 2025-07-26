"""
Authentication fixtures for integration tests.
Provides fixtures for user creation, registration, and login.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infra.models.user import User


@pytest.fixture(scope="session")
def test_user_data():
    """
    Test user data.
    
    这个fixture提供了测试用户的基本数据。
    使用随机email避免重复注册问题。
    """
    # 使用随机UUID生成唯一邮箱
    random_suffix = str(uuid.uuid4())[:8]
    return {
        "name": "Test User",
        "email": f"testuser_{random_suffix}@example.com",
        "password": "password123"
    }


@pytest.fixture(scope="session")
def registered_user(app_client, test_user_data):
    """
    Register a test user through the API.
    
    通过API注册一个测试用户，返回注册响应。
    """
    response = app_client.post(
        "/v1/auth/register",
        json=test_user_data
    )
    assert response.status_code in [200, 201], f"Failed to register user: {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def authenticated_user(test_db_session, registered_user):
    """
    Get the authenticated user from database.
    
    从数据库获取已认证的用户对象。
    """
    user_id = registered_user.get("id")
    assert user_id, "No id in registration response"
    
    user = test_db_session.query(User).filter(User.id == user_id).first()
    assert user, f"User with ID {user_id} not found in database"
    
    return user


@pytest.fixture(scope="session")
def authenticated_client(app_client, registered_user):
    """
    Get an authenticated client with auth headers.
    
    创建一个带有认证头的客户端，用于已认证的API请求。
    """
    access_token = registered_user.get("access_token")
    assert access_token, "No access_token in registration response"
    
    # 克隆一个新的client而不是修改原始client
    client = TestClient(app_client.app)
    client.headers.update({
        "Authorization": f"Bearer {access_token}"
    })
    
    return client 