"""
单元工作模式 (Unit of Work) 简化资源管理和事务处理

扩展了 SQLAlchemy 事务管理，支持跨数据库、向量数据库和缓存的一致性操作：
- 支持多种资源同时维护（数据库连接、向量数据库、缓存等）
- 自动提交/回滚管理，避免事务泄露
- 简化为单一依赖注入点
- 支持查询参数和通用头部处理
"""

import inspect
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional, TypeVar, Type, TYPE_CHECKING
from fastapi import Header, Depends
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import suppress

from app.core.db import get_db
from app.core.vector import get_vector_session
from app.core.vector.session import VectorSession
from app.core.redis import get_redis_client
from app.core.auth.jwt import verify_access_token
from app.core.exceptions.auth.invalid_token import InvalidTokenException
from app.core.exceptions.auth.unauthorized import UnauthorizedException
from app.infra.repo.user_repository import UserRepository
from app.infra.models import User
from app.infra.quota import QuotaBucket
from contextvars import Token
from .context import uow_ctx
from fastapi import WebSocket

class UnitOfWork:
    """Resource manager implementing unit-of-work pattern"""

    db: AsyncSession
    vector: VectorSession
    redis: redis.Redis
    current_user: "User"
    current_user_id: int
    accept_language: str
    target_language: str
    quota: QuotaBucket
    
    def __init__(self, **resources: Any) -> None:
        # 将资源同时存入私有 dict，并挂到实例属性上，便于外部通过 uow.db 直接访问
        self._resources: Dict[str, Any] = {}
        for key, resource in resources.items():
            setattr(self, key, resource)
            self._resources[key] = resource

    async def commit(self) -> None:
        """Iterate through resources and commit if possible."""
        # 逐个资源调用 commit；若资源无此方法则自动跳过
        await self._broadcast("commit")

    async def rollback(self) -> None:
        """Iterate through resources and rollback if possible."""
        # 出错时统一回滚，保持跨资源一致性
        await self._broadcast("rollback")

    async def close(self) -> None:
        """Iterate through resources and close if possible."""
        methods = [
            'aclose',
            'close'
        ]
        # 检测self._resources中是否存在
        for resource in self._resources.values():
            for method in methods:
                # 如果不存在对应方法，则跳过
                if not hasattr(resource, method):
                    continue
                # 如果存在对应方法，检测是否为异步方法，如果是则await，否则直接调用
                if inspect.iscoroutinefunction(getattr(resource, method)) or method == "aclose":
                    await getattr(resource, method)()
                    break
                else:
                    getattr(resource, method)()

    # Async context manager helpers

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()

    # Internal helpers

    # 通过string调用资源中的方法, 可以通用化
    async def _broadcast(self, method_name: str) -> None:
        """Call method_name on every resource if that method exists."""
        for resource in self._resources.values():
            # 若资源不存在对应方法则直接跳过
            method = getattr(resource, method_name, None)
            if method is None or not callable(method):
                continue

            # 兼容同步和异步方法，减少实现约束
            if inspect.iscoroutinefunction(method):
                await method()
            else:
                method()


# FastAPI dependency helper
async def get_uow(
    authorization: str | None = Header(default=None, alias="Authorization"),
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
    target_language: str | None = Header(default=None, alias="Target-Language"),
    db: AsyncSession = Depends(get_db),
    vector: VectorSession = Depends(get_vector_session),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Aggregate db, vector, and authenticated user context into a single unit-of-work
    object. If JWT is missing or invalid, raise 401 immediately.
    
    認証(にんしょう)トークンがない、または無効(むこう)の場合(ばあい)は 401 を返(かえ)します。
    """

    # 如果没有提供 Authorization 头，直接返回 401
    if authorization is None or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing bearer token")

    token = authorization.split(" ", 1)[1]

    try:
        payload = verify_access_token(token)
    except InvalidTokenException as exc:
        # 直接向上抛出，FastAPI 会转换为 JSON 响应
        raise UnauthorizedException("Invalid token") from exc

    # 提取用户 ID；payload 必须包含 sub 字段
    user_sub = payload.get("sub")
    if user_sub is None:
        raise UnauthorizedException("Token missing subject")

    try:
        user_id = int(user_sub)
    except ValueError:
        raise UnauthorizedException("Malformed subject in token")

    # 把user_id转换为user
    user_repo = UserRepository(db=db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    # 创建UoW实例，包含所有必要的资源
    uow = UnitOfWork(
        db=db, 
        vector=vector,
        redis=redis_client,
        # 当前认证用户
        current_user=user,
        # 请求头中的首选语言
        accept_language=accept_language,
        # 请求头中的目标语言
        target_language=target_language,
        # 用户配额
        quota=QuotaBucket(redis_client, user),
        # 当前用户ID
        current_user_id=user_id,
    )
    
    token = uow_ctx.set(uow)
    try:
        yield uow
        await uow.commit()
    except Exception as e:
        strerror = str(e)
        print(strerror)
        # 确保异常情况下也回滚
        await uow.rollback()
        raise
    finally:
        # 无论如何都要关闭资源
        uow_ctx.reset(token)
        await uow.close()


async def get_uow_ws(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    vector: VectorSession = Depends(get_vector_session),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> AsyncGenerator[UnitOfWork, None]:
    """
    WebSocket-compatible dependency to aggregate resources and auth.

    Token and language preferences are read from either headers or query params:
    - token: Authorization bearer token (without the "Bearer " prefix if passed as query)
    - accept_language: preferred UI language
    - target_language: target learning language
    """

    # Prefer header Authorization if present; otherwise read from query
    auth_header = websocket.headers.get("authorization")
    token: str | None = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = websocket.query_params.get("token")

    if not token:
        raise UnauthorizedException("Missing bearer token")

    try:
        payload = verify_access_token(token)
    except InvalidTokenException as exc:
        raise UnauthorizedException("Invalid token") from exc

    user_sub = payload.get("sub")
    if user_sub is None:
        raise UnauthorizedException("Token missing subject")

    try:
        user_id = int(user_sub)
    except ValueError:
        raise UnauthorizedException("Malformed subject in token")

    user_repo = UserRepository(db=db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    # Languages from headers or query params
    accept_language = websocket.query_params.get("accept-language") or websocket.headers.get("accept-language")
    target_language = websocket.query_params.get("target-language") or websocket.headers.get("target-language")

    uow = UnitOfWork(
        db=db,
        vector=vector,
        redis=redis_client,
        current_user=user,
        accept_language=accept_language,
        target_language=target_language,
        quota=QuotaBucket(redis_client, user),
        current_user_id=user_id,
    )

    token_ctx: Token = uow_ctx.set(uow)
    try:
        yield uow
        # Let caller decide commit timing; default to commit when scope ends
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        uow_ctx.reset(token_ctx)
        await uow.close()