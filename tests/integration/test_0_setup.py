"""
Basic tests to verify the test setup is working correctly.
These tests validate the environment configuration and database connectivity.
"""
import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from app.main import app


def test_app_client(app_client):
    """Test that the app client is initialized correctly."""
    response = app_client.get("/v1/health", headers={"Content-Type": "application/json"})
    assert response.status_code == 200, f"Failed to access health endpoint: {response.text}"


def test_db_session(test_db_session):
    """Test that the database session is working."""
    # 简单验证session是否可用
    result = test_db_session.execute(text("SELECT 1")).scalar()
    assert result == 1, "Database session is not working correctly"


def test_dependencies_initialized():
    """Test that all required dependencies are initialized."""
    # 验证应用状态中的关键依赖
    assert hasattr(app.state, "async_session_maker"), "async_session_maker not initialized"
    assert hasattr(app.state, "qdrant_client"), "qdrant_client not initialized"
    assert hasattr(app.state, "redis_client"), "redis_client not initialized" 