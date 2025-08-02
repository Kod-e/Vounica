"""
Authentication tests to verify user registration and login functionality.
"""
import pytest


@pytest.mark.order(1)
async def test_user_registration(registered_user):
    """Test that a user can be registered successfully."""
    # 使用共享的registered_user fixture而不是直接调用API注册
    data = registered_user
    assert "id" in data, "User ID not returned in registration response"
    assert "email" in data, "Email not returned in registration response"
    assert "access_token" in data, "No access token in response"
    assert "refresh_token" in data, "No refresh token in response"


@pytest.mark.order(2)
async def test_user_login(async_client):
    """Test that a registered user can login successfully."""
    # 首先注册一个用户
    register_data = {
        "name": "Login Test User",
        "email": "logintest@example.com",
        "password": "password123"
    }
    
    # 注册用户
    register_response = await async_client.post(
        "/v1/auth/register",
        json=register_data
    )
    assert register_response.status_code == 200, f"Failed to register user: {register_response.text}"
    
    # 然后尝试登录
    login_data = {
        "email": "logintest@example.com",
        "password": "password123"
    }
    
    response = await async_client.post(
        "/v1/auth/login",
        json=login_data
    )
    
    assert response.status_code == 200, f"Failed to login: {response.text}"
    data = response.json()
    
    # 验证返回的令牌数据
    assert "access_token" in data, "No access token in response"
    assert "refresh_token" in data, "No refresh token in response"

@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_authenticated_async_client(registered_user, async_client):
    """
    Test that the authenticated_async_client fixture works properly.
    
    测试异步认证客户端是否正常工作。
    """
    # 使用注册用户的access_token设置认证头
    access_token = registered_user.get("access_token")
    assert access_token, "No access_token in registration response"
    
    # 设置异步客户端的认证头
    async_client.headers["Authorization"] = f"Bearer {access_token}"
    
    # 测试访问需要认证的端点
    response = await async_client.get("/v1/user/me")
    assert response.status_code == 200, f"Failed to access protected endpoint: {response.text}"
    
    # 验证返回的用户信息
    data = response.json()
    assert "email" in data
    assert data["email"] == registered_user.get("email")


@pytest.mark.order(3)
async def test_unauthorized_access_to_refresh(async_client):
    """Test that unauthorized access to refresh token endpoint is properly rejected."""
    # 尝试在没有认证的情况下刷新token
    response = await async_client.post(
        "/v1/auth/refresh", 
        json={"refresh_token": "invalid_token"}
    )
    assert response.status_code in [401, 403, 400], f"Expected error but got: {response.status_code}" 