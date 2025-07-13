from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.api.v1.router import router as v1_router

# 配置数据库 URL (建议实际项目中通过环境变量或配置文件加载)
DATABASE_URL = "mysql+aiomysql://user:password@localhost:3306/vounica"

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
app.include_router(v1_router, prefix="/api/v1")

# 健康检查端点
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 