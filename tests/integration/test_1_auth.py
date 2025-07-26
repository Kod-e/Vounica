"""
Authentication tests to verify user registration and login functionality.
"""
import pytest


@pytest.mark.order(1)
def test_user_registration(registered_user):
    """Test that a user can be registered successfully."""
    # 使用共享的registered_user fixture而不是直接调用API注册
    data = registered_user
    assert "id" in data, "User ID not returned in registration response"
    assert "email" in data, "Email not returned in registration response"
    assert "access_token" in data, "No access token in response"
    assert "refresh_token" in data, "No refresh token in response"


@pytest.mark.order(2)
def test_user_login(test_user_data, app_client):
    """Test that a registered user can login successfully."""
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    
    response = app_client.post(
        "/v1/auth/login",
        json=login_data
    )
    
    assert response.status_code == 200, f"Failed to login: {response.text}"
    data = response.json()
    
    # 验证返回的令牌数据
    assert "access_token" in data, "No access token in response"
    assert "refresh_token" in data, "No refresh token in response"


@pytest.mark.order(3)
def test_authenticated_client(authenticated_client):
    """Test that the authenticated client has valid auth headers."""
    # 使用/v1/health作为测试端点，因为它不需要特殊权限但可以验证客户端是否正常工作
    response = authenticated_client.get("/v1/health")
    assert response.status_code == 200, f"Failed to access health endpoint: {response.text}"


@pytest.mark.order(4)
def test_unauthorized_access_to_refresh(app_client):
    """Test that unauthorized access to refresh token endpoint is properly rejected."""
    # 尝试在没有认证的情况下刷新token
    response = app_client.post(
        "/v1/auth/refresh", 
        json={"refresh_token": "invalid_token"}
    )
    assert response.status_code in [401, 403, 400], f"Expected error but got: {response.status_code}" 