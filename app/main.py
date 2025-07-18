from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.api.v1.router import router as v1_router

# ---------------------------------------------------------------
# 数据库连接 URL
#   1. 首先通过 python-dotenv 读取 .env（方便本地开发）
#   2. 然后从环境变量 DATABASE_URL 获取；若不存在则降级到默认值
# ---------------------------------------------------------------

# 读取 .env 文件变量
load_dotenv()

# 从环境变量获取数据库 URL；如果没有配置则使用默认值
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://user:password@localhost:3306/vounica",
)

# 全局变量，用于存储引擎和会话工厂
engine = None
async_session_maker = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用程序生命周期管理
    启动时创建数据库引擎和会话工厂，关闭时释放资源
    """
    global engine, async_session_maker
    
    # 启动时创建引擎和会话工厂
    print("正在启动应用，创建数据库连接...")
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # 设置为True可查看SQL语句
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    async_session_maker = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    yield
    
    # 关闭时释放资源
    print("正在关闭应用，释放数据库连接...")
    if engine:
        await engine.dispose()


# 创建FastAPI应用实例
app = FastAPI(
    title="Vounica API",
    description="Vounica 应用程序 API",
    version="0.1.0",
    lifespan=lifespan,
)

# 注册路由
app.include_router(v1_router, prefix="/v1")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 