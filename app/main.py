from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os
import uvicorn
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.api.v1.router import router as v1_router

from app.core.vector import make_qdrant_client
from app.core.db import make_async_session_maker, get_engine, check_table_exists
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
    # 检测数据库内是否存在表
    if not await check_table_exists():
        print("Database tables do not exist, creating tables...")
        from scripts.init_db import init_db, init_collections
        await init_db()
        await init_collections()
    # 将引擎和会话工厂注入到app的state中
    app.state.async_session_maker = async_session_maker
    app.state.qdrant_client = qdrant_client
    app.state.redis_client = redis_client
    yield
    # 关闭时释放资源
    print("Application is shutting down...")
    
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

    # CORS 配置
    cors_origins_env = os.getenv("CORS_ORIGINS")
    if cors_origins_env and cors_origins_env.strip():
        try:
            import json
            parsed = json.loads(cors_origins_env)
            if isinstance(parsed, list):
                allow_origins = [str(origin).strip() for origin in parsed if str(origin).strip()]
            else:
                allow_origins = [o.strip() for o in str(cors_origins_env).split(",") if o.strip()]
        except Exception:
            allow_origins = [o.strip() for o in str(cors_origins_env).split(",") if o.strip()]
        allow_credentials = True
    else:
        allow_origins = ["*"]
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(v1_router, prefix="/v1")
    app.include_router(health_router, prefix="/health")
    return app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("UVICORN_HOST", "0.0.0.0")
    port = int(os.getenv("UVICORN_PORT", "8000"))
    reload_flag = str(os.getenv("UVICORN_RELOAD", "false")).strip().lower() in {"1", "true", "yes", "on"}
    uvicorn.run("app.main:app", host=host, port=port, reload=reload_flag) 