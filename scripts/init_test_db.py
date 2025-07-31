#!/usr/bin/env python3

"""
测试数据库初始化脚本
用于创建测试环境的数据库表结构
"""
import asyncio
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径，确保可以导入app模块
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# 现在可以导入app模块
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.db.base import Base

# 导入所有模型类，确保它们被SQLAlchemy的元数据注册
# 这些导入不会被使用，但它们会触发模型类的注册
from app.infra.models.user import User
from app.infra.models.vocab import Vocab
from app.infra.models.grammar import Grammar
from app.infra.models.memory import Memory
from app.infra.models.mistake import Mistake
from app.infra.models.refresh_token import RefreshToken
from app.infra.models.story import Story
from app.infra.vector.collections import COLLECTIONS_CONFIG
from app.core.vector.provider import make_qdrant_client
# 或者可以直接导入所有模型
# from app.infra.models import *

# 测试配置常量 - 使用非标准端口避免与本地开发环境冲突
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:15432/test_vounica"
# 用于同步操作（如创建表）的URL
TEST_SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:15432/test_vounica"
# 测试向量数据库连接 URL
TEST_QDRANT_URL = "http://localhost:16333"

async def init_test_db():
    """
    Initialize the test database.
    """
    print("Initializing the test database...")
    
    # 从环境变量获取测试数据库连接URL，如果没有设置则使用默认值
    database_url = os.getenv("TEST_DATABASE_URL", TEST_DATABASE_URL)
    
    print(f"Using database URL: {database_url}")
    
    # 打印元数据中的表名称
    tables = [table.name for table in Base.metadata.sorted_tables]
    print(f"Tables to be created: {', '.join(tables)}")
    
    # 创建引擎
    engine = create_async_engine(
        database_url,
        echo=True  # 显示 SQL 语句
    )
    
    # 创建会话工厂
    async_session_maker = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 清理连接池
    await engine.dispose()
    
    # 初始化collections
    os.environ["QDRANT_URL"] = TEST_QDRANT_URL
    qdrant_client = make_qdrant_client()
    for collection, params in COLLECTIONS_CONFIG.items():
        if not qdrant_client.collection_exists(collection):
            qdrant_client.create_collection(
                collection_name=collection.value,
                vectors_config=params
            )
        else:
            print(f"Collection {collection} already exists!")
            
    print("Test database initialized successfully!")


async def drop_test_db():
    """
    Drop all tables in the test database.
    """
    print("Dropping all tables in the test database...")
    
    # 从环境变量获取测试数据库连接URL，如果没有设置则使用默认值
    database_url = os.getenv("TEST_DATABASE_URL", TEST_DATABASE_URL)
    
    print(f"Using database URL: {database_url}")
    
    # 创建引擎
    engine = create_async_engine(database_url, echo=True)
    
    # 删除所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # 清理连接池
    await engine.dispose()
    
    # 删除collections
    qdrant_client = make_qdrant_client()
    os.environ["QDRANT_URL"] = TEST_QDRANT_URL
    for collection in COLLECTIONS_CONFIG.keys():
        if qdrant_client.collection_exists(collection.value):
            qdrant_client.delete_collection(collection.value)
        else:
            print(f"Collection {collection} not found!")
    
    print("All tables dropped successfully!")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Initialize test database for Vounica")
    parser.add_argument("--drop-all", action="store_true", help="Drop all tables before creating them")
    parser.add_argument("--env-file", default="test.env", help="Environment file to load (default: test.env)")
    args = parser.parse_args()
    
    # 加载环境变量
    print(f"Loading environment from {args.env_file}...")
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
    else:
        print(f"Warning: Environment file '{args.env_file}' not found, using default values")
    
    # 如果需要先删除所有表
    if args.drop_all:
        asyncio.run(drop_test_db())
    
    # 初始化测试数据库
    asyncio.run(init_test_db()) 