"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.db import Base  # get_db 未使用，移除以避免循环依赖警告
from app.models import *
# 加载环境变量
load_dotenv()

# 数据库连接 URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/vounica")

async def init_db():
    """
    Initialize the database.
    """
    print("Initializing the database...")
    
    # 创建引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True  # 显示 SQL 语句
    )
    
    # 创建会话工厂
    async_session_maker = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    async with engine.begin() as conn:
        # 创建所有表
        from app.core.db.base import Base
        await conn.run_sync(Base.metadata.create_all)
    
    
    # 关闭引擎
    await engine.dispose()
    
    print("Database initialized successfully!")


if __name__ == "__main__":
    # 运行初始化函数
    asyncio.run(init_db()) 