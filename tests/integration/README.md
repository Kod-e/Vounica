# Vounica 集成测试框架

## 概述

本测试框架基于黑盒测试原则设计，通过实际API调用而非内部操作进行测试，确保测试尽可能接近真实用户体验。测试默认使用Docker容器提供隔离的测试环境，并支持完整的用户旅程测试流程。

## 测试架构

```
tests/
  └── integration/
      ├── conftest.py         # 基础设施设置（Docker、应用初始化）
      ├── auth_fixtures.py    # 用户认证相关fixture
      ├── test_setup.py       # 基本环境测试
      └── README.md           # 测试文档
```

## 测试流程

1. **基础设施初始化** (conftest.py)
   - 默认启动Docker服务（PostgreSQL、Redis、Qdrant）
   - 设置测试环境变量
   - 按照app.main.py中的方式初始化应用依赖
   - 创建FastAPI测试客户端

2. **用户认证** (auth_fixtures.py)
   - 注册测试用户（module级别）
   - 登录获取JWT访问令牌（module级别）
   - 创建已认证的HTTP客户端（module级别）

3. **基本测试** (test_setup.py)
   - 验证应用客户端正常工作
   - 验证数据库会话正常工作
   - 验证所有依赖正确初始化

## 设计原则

1. **黑盒测试**：通过公开API进行测试，而不是内部组件
2. **模拟真实用户**：所有测试操作都是真实用户可能执行的HTTP请求
3. **共享状态**：整个测试旅程中保持用户状态
4. **依赖注入**：应用自身负责依赖注入，测试不干预这个过程
5. **环境隔离**：使用非标准端口避免与开发环境冲突

## 环境配置

测试环境使用非标准端口，避免与本地开发环境冲突：

```
# 数据库
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:15432/test_vounica"

# Redis
TEST_REDIS_URL = "redis://localhost:16379/1"

# Qdrant
TEST_QDRANT_URL = "http://localhost:16333"
```

这些配置在`docker-compose.test.yml`、`conftest.py`和`test.env`中保持一致。

## 运行测试

```bash
# 默认使用Docker（推荐方式）
python -m pytest tests/integration/ -v

# 使用本地服务（不启动Docker）
python -m pytest tests/integration/ -v --local

# 运行单个测试文件
python -m pytest tests/integration/test_setup.py -v

# 运行特定测试方法
python -m pytest tests/integration/test_setup.py::test_app_client -v
```

## 使用VS Code调试

VS Code中提供了多种调试配置：

1. **Run Integration Tests** - 使用Docker运行所有集成测试
2. **Run Integration Tests (Local)** - 使用本地服务运行所有集成测试
3. **Run Current Test** - 使用Docker运行当前打开的测试文件
4. **Run Current Test (Local)** - 使用本地服务运行当前打开的测试文件

## 编写新测试

添加新的集成测试时，请遵循以下步骤：

1. 在`tests/integration/`目录下创建新的测试文件，命名为`test_*.py`
2. 如需要用户认证，使用`authenticated_client`和`authenticated_user` fixtures
3. 如果测试需要按顺序执行，使用`@pytest.mark.order()`装饰器
4. 保持黑盒测试原则，通过API调用而非直接操作内部组件
5. 共用一个测试用户，避免在测试中重复创建用户

例如：

```python
import pytest

def test_some_feature(authenticated_client, authenticated_user):
    """Test some application feature."""
    response = authenticated_client.get(f"/v1/some-endpoint/{authenticated_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
``` 