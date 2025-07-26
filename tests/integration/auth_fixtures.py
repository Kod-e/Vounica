"""
Authentication fixtures for integration tests.
Provides fixtures for user creation, registration, and login.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infra.models.user import User


@pytest.fixture(scope="module")
def test_user_data():
    """
    Test user data.
    
    这个fixture提供了测试用户的基本数据。
    """
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123"
    }


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def user_token(app_client, test_user_data, registered_user):
    """
    Get a user token by logging in.
    
    通过登录获取用户token。
    使用已经注册的用户（从registered_user fixture）。
    """
    # 登录获取token
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    
    # 登录获取token
    response = app_client.post(
        "/v1/auth/login",
        json=login_data
    )
    
    assert response.status_code == 200, f"Failed to login: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access token in response"
    return data


@pytest.fixture(scope="module")
def authenticated_user(test_db_session, user_token):
    """
    Get the authenticated user from database.
    
    从数据库获取已认证的用户对象。
    """
    user_id = user_token.get("user_id")
    assert user_id, "No user_id in token response"
    
    user = test_db_session.query(User).filter(User.id == user_id).first()
    assert user, f"User with ID {user_id} not found in database"
    
    return user


@pytest.fixture(scope="module")
def authenticated_client(app_client, user_token):
    """
    Get an authenticated client with auth headers.
    
    创建一个带有认证头的客户端，用于已认证的API请求。
    """
    access_token = user_token.get("access_token")
    assert access_token, "No access_token in token response"
    
    # 创建一个新的client，并添加认证头
    app_client.headers.update({
        "Authorization": f"Bearer {access_token}"
    })
    
    return app_client 