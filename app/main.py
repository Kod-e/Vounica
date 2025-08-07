from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os
import uvicorn
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from fastapi import FastAPI, APIRouter


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.api.v1.router import router as v1_router

from app.core.vector import make_qdrant_client
from app.core.db import make_async_session_maker, get_engine
from app.core.redis import make_redis_client

# 加载环境变量
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用程序生命周期管理
    启动时创建数据库引擎和会话工厂，关闭时释放资源
    """

    # 启动时创建引擎和会话工厂
    async_session_maker = make_async_session_maker()
    qdrant_client = make_qdrant_client()
    redis_client = make_redis_client()
    # 将引擎和会话工厂注入到app的state中
    app.state.async_session_maker = async_session_maker
    app.state.qdrant_client = qdrant_client
    app.state.redis_client = redis_client
    yield
    # 关闭时释放资源
    print("正在关闭应用，释放数据库连接...")
    
    # 关闭SQLAlchemy的连接池+
    await get_engine().dispose()
    qdrant_client.close()
    await redis_client.aclose()

# 健康检查端点
health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    return {"status": "healthy"}

def create_app() -> FastAPI:
    # 创建FastAPI应用实例
    app = FastAPI(
        title="Vounica API",
        description="Vounica API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 注册路由
    app.include_router(v1_router, prefix="/v1")
    app.include_router(health_router, prefix="/health")
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 