"""
用于调试JWT配置的简单测试脚本
"""
import os
import pytest
from app.core.auth.jwt import create_access_token, verify_access_token, IS_TEST, ALGORITHM

def test_jwt_configuration():
    """测试JWT配置是否正确设置"""
    # 验证测试模式已正确设置
    assert IS_TEST is True, "TEST_MODE环境变量未正确设置"
    
    # 验证算法已正确设置为HS256
    assert ALGORITHM == "HS256", f"JWT算法应为HS256，但实际为{ALGORITHM}"
    
    # 创建并验证一个令牌
    user_id = 123
    token = create_access_token(user_id)
    payload = verify_access_token(token)
    
    # 验证payload中包含正确的user_id
    assert payload["sub"] == str(user_id), f"Token payload中的sub应为'{user_id}'，但实际为'{payload['sub']}'"
    
    print("JWT配置测试成功！")
    print(f"算法: {ALGORITHM}")
    print(f"测试模式: {IS_TEST}")
    print(f"令牌: {token}")
    
    return True 