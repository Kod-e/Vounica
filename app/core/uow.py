from __future__ import annotations
from typing import Any, Dict, AsyncGenerator, TYPE_CHECKING
import inspect

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.base import get_db
from app.core.vector.session import VectorSession, get_vector_session


class UnitOfWork:  # pylint: disable=too-few-public-methods
    """Forward commit / rollback / close 操作到所有注入的资源。"""

    # 类型
    if TYPE_CHECKING:
        db: AsyncSession
        vector: VectorSession

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
    db: AsyncSession = Depends(get_db),
    vector: VectorSession = Depends(get_vector_session),
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Aggregate db and vector into a single unit-of-work object.
    """

    uow = UnitOfWork(db=db, vector=vector)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close() 