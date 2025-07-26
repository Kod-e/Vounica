import subprocess
import os
import time
import pytest
import socket
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from app.main import app
from app.core.db.base import Base
from app.core.vector.provider import make_qdrant_client
from app.core.db.provider import make_async_session_maker
from app.core.redis.provider import make_redis_client

# 导入auth_fixtures中的所有fixtures
from .auth_fixtures import *

# 测试配置常量 - 使用非标准端口避免与本地开发环境冲突
DOCKER_COMPOSE_FILE = "docker-compose.test.yml"
# 使用asyncpg作为异步驱动
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:15432/test_vounica"
# 用于同步操作（如创建表）的URL
TEST_SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:15432/test_vounica"
TEST_REDIS_URL = "redis://localhost:16379/1"
TEST_QDRANT_URL = "http://localhost:16333"

def is_port_open(host, port, timeout=1):
    """检查指定端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def wait_for_services():
    """等待所有服务准备就绪"""
    print("等待服务准备就绪...")
    
    # 定义最大等待时间（秒）和检查间隔
    max_wait = 60
    interval = 1
    
    # 等待PostgreSQL
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_port_open("localhost", 15432):
            print("PostgreSQL 已就绪")
            break
        time.sleep(interval)
    else:
        raise TimeoutError("等待PostgreSQL超时")
    
    # 等待Redis
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_port_open("localhost", 16379):
            print("Redis 已就绪")
            break
        time.sleep(interval)
    else:
        raise TimeoutError("等待Redis超时")
    
    # 等待Qdrant
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_port_open("localhost", 16333):
            print("Qdrant 已就绪")
            break
        time.sleep(interval)
    else:
        raise TimeoutError("等待Qdrant超时")
    
    # 额外等待一点时间，确保服务完全初始化
    time.sleep(3)
    print("所有服务已就绪")

def pytest_addoption(parser):
    """Add command line options for testing."""
    parser.addoption(
        "--local", action="store_true", default=False,
        help="Use local services instead of starting Docker containers"
    )

def pytest_sessionstart(session):
    """Start docker services if not running in local mode."""
    # 默认使用Docker，只有--local参数时才不启动Docker
    if not session.config.getoption("--local"):
        print("Starting docker services...")
        try:
            subprocess.run(
                ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d", "--force-recreate", "--remove-orphans"],
                check=True
            )
            
            # 等待所有服务准备就绪
            wait_for_services()
        except Exception as e:
            print(f"启动Docker服务失败: {e}")
            print("如果您已经在本地运行了测试服务，请使用 --local 参数运行测试")
            raise
    else:
        print("使用本地服务（不启动Docker容器）")
        # 如果使用本地服务，检查服务是否可用
        if not all([
            is_port_open("localhost", 15432),
            is_port_open("localhost", 16379),
            is_port_open("localhost", 16333)
        ]):
            print("警告：部分测试服务不可用，测试可能会失败")
    
    # 设置测试环境变量
    os.environ["TEST_MODE"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL  # 使用异步URL
    os.environ["REDIS_URL"] = TEST_REDIS_URL
    os.environ["QDRANT_URL"] = TEST_QDRANT_URL
    
    try:
        # 初始化同步引擎用于测试和表创建（这里仍需要同步引擎创建表）
        print("正在初始化测试数据库...")
        engine = create_engine(TEST_SYNC_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("测试数据库初始化成功")
    except Exception as e:
        print(f"初始化测试数据库失败: {e}")
        print("请确保PostgreSQL服务在端口15432上运行")
        raise

def pytest_sessionfinish(session, exitstatus):
    """Stop docker services after tests complete if not in local mode."""
    if not session.config.getoption("--local"):
        print("Stopping docker services...")
        try:
            subprocess.run(
                ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down", "-v"],
                check=True
            )
        except Exception as e:
            print(f"停止Docker服务失败: {e}")

# 初始化应用依赖，模拟app.main.py中的lifespan函数
@pytest.fixture(scope="session", autouse=True)
def setup_test_dependencies():
    """
    Initialize all dependencies before testing, similar to app.main.py lifespan.
    这会按照app.main.py中的方式初始化所有依赖，保证测试环境与实际应用环境一致。
    """
    print("Setting up test dependencies...")
    
    # 设置测试环境变量
    os.environ["TEST_MODE"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["REDIS_URL"] = TEST_REDIS_URL
    os.environ["QDRANT_URL"] = TEST_QDRANT_URL
    
    # 按照app.main.py中的方式初始化依赖
    try:
        # 1. 创建会话工厂
        async_session_maker = make_async_session_maker(TEST_DATABASE_URL)
        
        # 2. 创建其他客户端
        qdrant_client = make_qdrant_client()
        redis_client = make_redis_client(TEST_REDIS_URL)
        
        # 保存在全局状态中以供测试使用
        app.state.async_session_maker = async_session_maker
        app.state.qdrant_client = qdrant_client
        app.state.redis_client = redis_client
        
        print("Test dependencies initialized.")
    except Exception as e:
        print(f"Failed to initialize dependencies: {e}")
        raise
    
    yield
    
    # 测试结束后清理资源
    print("Cleaning up test resources...")

# 同步会话工厂，用于测试中的直接数据库操作（不通过API）
@pytest.fixture(scope="module")
def test_db_session_factory():
    """Create a SQLAlchemy session factory for testing."""
    engine = create_engine(TEST_SYNC_DATABASE_URL)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db_session(test_db_session_factory):
    """
    Create a SQLAlchemy session for testing.
    
    使用module作用域保证在同一测试模块中共享数据库会话。
    这个会话只用于测试中需要直接查询数据库的场景，不应用于模拟API请求。
    """
    session = test_db_session_factory()
    try:
        yield session
    finally:
        # 在module结束时才提交或回滚，保持整个测试模块的事务一致性
        session.rollback()
        session.close()

@pytest.fixture(scope="module")
def app_client():
    """
    Create a FastAPI TestClient.
    
    这个TestClient会使用应用自身的依赖注入机制，
    正如一个真实的HTTP客户端那样工作。
    """
    # 确保依赖已初始化
    assert hasattr(app.state, "async_session_maker"), "Async session maker not initialized"
    
    with TestClient(app) as client:
        yield client