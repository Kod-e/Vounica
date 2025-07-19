"""
Common BaseService providing transactional CRUD and vector synchronization.

モデル共通(きょうつう)の CRUD + ベクター処理(しょり)をまとめた Service 基底(きてい)。
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from app.core.uow import UnitOfWork
from app.core.db.base import BaseModel
from app.core.db.repository import Repository
from app.infra.vector.operations import (
    queue_vector_from_instance,
    queue_vector_delete_for_instance,
)

# 类型参数: 受 BaseModel 约束
T = TypeVar("T", bound=BaseModel)


class BaseService(Generic[T]):  # pylint: disable=too-few-public-methods
    """High-level CRUD helper bound to a specific repository.

    DB 操作と Qdrant ベクター操作を同一(どういつ) UnitOfWork で扱(あつか)います。
    """

    def __init__(self, repository: Repository[T]):
        self._repo: Repository[T] = repository

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    async def get(self, uow: UnitOfWork, id_: Any) -> Optional[T]:
        return await self._repo.get_by_id(uow.db, id_)

    async def list(self, uow: UnitOfWork, *, skip: int = 0, limit: int = 100) -> List[T]:
        return await self._repo.get_all(uow.db, skip=skip, limit=limit)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    async def create(self, uow: UnitOfWork, data: Dict[str, Any]) -> T:  # type: ignore[type-var]
        instance: T = await self._repo.create(uow.db, data)
        queue_vector_from_instance(instance, uow.vector)
        return instance

    async def update(self, uow: UnitOfWork, id_: Any, data: Dict[str, Any]) -> Optional[T]:
        instance = await self._repo.update(uow.db, id_, data)
        if instance is not None:
            queue_vector_from_instance(instance, uow.vector)
        return instance

    async def delete(self, uow: UnitOfWork, id_: Any) -> Optional[T]:
        # 先获取实例, 用于删除对应向量
        instance = await self._repo.get_by_id(uow.db, id_)
        if instance is None:
            return None

        # 删除向量
        queue_vector_delete_for_instance(instance, uow.vector)
        # 删除数据库记录
        deleted = await self._repo.delete(uow.db, id_)
        return deleted 