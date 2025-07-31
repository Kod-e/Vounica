"""
Common BaseService providing transactional CRUD and vector synchronization.

モデル共通(きょうつう)の CRUD + ベクター処理(しょり)をまとめた Service 基底(きてい)。
"""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from app.infra.context import uow_ctx
from app.infra.uow  import UnitOfWork
from app.core.db.base import BaseModel
from app.core.db.repository import Repository
from app.infra.vector.operations import (
    queue_vector_from_instance,
    queue_vector_delete_for_instance
)

# 类型参数: 受 BaseModel 约束
T = TypeVar("T", bound=BaseModel)


class BaseService(Generic[T]):  # pylint: disable=too-few-public-methods
    """High-level CRUD helper bound to a specific repository.

    DB 操作と Qdrant ベクター操作を同一(どういつ) UnitOfWork で扱(あつか)います。
    """

    def __init__(self, repository: Repository[T]):
        self._repo: Repository[T] = repository
        self._uow = uow_ctx.get()

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    async def get(self, id_: Any) -> Optional[T]:
        return await self._repo.get_by_id(self._uow.db, id_)

    async def list(self, offset: int = 0, limit: int = 100) -> List[T]:
        return await self._repo.get_all(self._uow.db, offset=offset, limit=limit)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    async def create(self, data: Dict[str, Any]) -> T:  # type: ignore[type-var]
        # 修复user_id不在create方法中的问题
        if "user_id" not in data:
            data["user_id"] = self._uow.current_user_id
        instance: T = await self._repo.create(self._uow.db, data)
        queue_vector_from_instance(instance, self._uow.vector)
        return instance

    async def update(self, data: Dict[str, Any]) -> Optional[T]:
        _id = data.pop("id")
        instance = await self._repo.update(self._uow.db, _id, data)
        if instance is not None:
            queue_vector_from_instance(instance, self._uow.vector)
        return instance

    async def delete(self, id_: Any) -> Optional[T]:
        # 先获取实例, 用于删除对应向量
        instance = await self._repo.get_by_id(self._uow.db, id_)
        if instance is None:
            return None

        # 删除向量
        queue_vector_delete_for_instance(instance, self._uow.vector)
        # 删除数据库记录
        deleted = await self._repo.delete(self._uow.db, id_)
        return deleted 