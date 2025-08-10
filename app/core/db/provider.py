"""
Hold and inject SQLAlchemy async session maker globally.

非同期(ひどうき) SQLAlchemy SessionMaker を保管(ほかん)し、外部(がいぶ)から注入(ちゅうにゅう)できるようにします。
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from dotenv import load_dotenv
import os
from sqlalchemy import text
from sqlalchemy.inspection import inspect

_session_maker: async_sessionmaker[AsyncSession] | None = None
_engine: AsyncEngine | None = None

def set_async_session_maker(maker: async_sessionmaker[AsyncSession]) -> None:
    """Inject a session maker from application layer."""
    global _session_maker
    _session_maker = maker

def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Retrieve the stored session maker or raise if not set."""
    if _session_maker is None:
        raise RuntimeError(
            "AsyncSession maker not set. Call set_async_session_maker() during application startup."
        )
    return _session_maker

def get_engine() -> AsyncEngine:
    """Retrieve the stored engine or raise if not set."""
    if _engine is None:
        raise RuntimeError(
            "AsyncEngine not set. Call make_async_session_maker() during application startup."
        )
    return _engine

def set_engine(engine: AsyncEngine) -> None:
    """Inject an engine from application layer."""
    global _engine
    _engine = engine

# ------------------------------------------------------------------
# Factory helper
# ------------------------------------------------------------------


def make_async_session_maker(database_url: str | None = None, **engine_kwargs) -> async_sessionmaker[AsyncSession]:
    """
    Create an async SQLAlchemy engine & session maker, then inject the session maker.

    非同期(ひどうき) database engine と session maker を作成(さくせい)し、provider に注入(ちゅうにゅう)します。
    """
    load_dotenv()

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "mysql+aiomysql://user:password@localhost:3306/vounica",
        )

    # 默认参数创建
    default_kwargs = dict(
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    default_kwargs.update(engine_kwargs)
    
    engine: AsyncEngine = create_async_engine(database_url, **default_kwargs)
    # 检测是否数据库内存在表, 不存在则创建
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # 设置session maker
    set_async_session_maker(session_maker)
    set_engine(engine)
    return session_maker 
async def check_table_exists(engine: AsyncEngine = None):
    if engine is None:
        engine = get_engine()
    # 检测是否数据库内存在表, 不存在则创建
    async with engine.connect() as conn:
        def _check(sync_conn):
            insp = inspect(sync_conn)
            # Inspector.has_table 跨方言可用；schema 对 PG 常用 'public'，MySQL 传 None
            return insp.has_table("users")
        return await conn.run_sync(_check)