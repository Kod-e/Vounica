from __future__ import annotations
from typing import Any, Dict, AsyncGenerator, TYPE_CHECKING
import inspect

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.base import get_db
from app.core.vector.session import VectorSession, get_vector_session
from app.core.auth.jwt import verify_access_token
from app.core.exceptions.auth.unauthorized import UnauthorizedException
from app.core.exceptions.auth.invalid_token import InvalidTokenException

if TYPE_CHECKING:
    from app.infra.models.user import User

class UnitOfWork:  # pylint: disable=too-few-public-methods
    """Forward commit / rollback / close 操作到所有注入的资源。"""

    # 类型
    if TYPE_CHECKING:
        db: AsyncSession
        vector: VectorSession
        user: 'User'

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
        # 收尾清理，释放连接 / 句柄
        await self._broadcast("close")

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
    db: AsyncSession = Depends(get_db),
    vector: VectorSession = Depends(get_vector_session),
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
    from app.infra.repo.user_repository import UserRepository
    user_repository = UserRepository()
    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("User not found")
    # 将 user_id 注入到 uow，方便下游逻辑使用
    uow = UnitOfWork(db=db, vector=vector, user=user)

    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close() 