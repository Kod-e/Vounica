"""
Vector session wrapper providing transactional-like behavior for Qdrant operations.

Qdrant への操作(そうさ)をトランザクション風(ふう)に扱(あつか)うためのラッパーです。
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, AsyncGenerator

from .provider import get_qdrant_client

# 类型别名，方便后续扩展
VectorOperation = Tuple[str, Dict[str, Any]]


class VectorSession:
    """
    Collect vector operations and flush them to Qdrant in one batch when
    `commit()` is called. If an exception occurs before commit, operations are
    discarded so SQL and vector data stay consistent.

    ベクター操作(そうさ)をためて、`commit()` で一度(いちど)に Qdrant へ送(おく)ります。
    例外(れいがい)が起(お)きたら捨(す)てます。
    """

    def __init__(self):
        # 每个会话持有独立操作列表，避免并发污染
        self._operations: List[VectorOperation] = []
        # 延迟获取 client，避免在 import 阶段就建立连接
        self._client = None

    # --------------------------- public API ---------------------------

    def add_point(self, collection_name: str, point: Dict[str, Any]) -> None:
        """Queue a single point to be upserted into the collection."""
        self._operations.append(
            (
                "upsert",
                {
                    "collection_name": collection_name,
                    "points": [point],  # stored as list for consistent API
                },
            )
        )

    def add_points(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        """Queue multiple points for upsert in a single operation."""
        if not points:
            return  # 避免空操作浪费
        self._operations.append(
            (
                "upsert",
                {
                    "collection_name": collection_name,
                    "points": points,
                },
            )
        )

    # -----------------------------------------------------------------
    # Delete helpers
    # -----------------------------------------------------------------

    def delete_by_filter(self, collection_name: str, filter_: Dict[str, Any]) -> None:
        """Queue deletion of points that match the given Qdrant filter.

        Args:
            collection_name: Target Qdrant collection.
            filter_: Qdrant filter dict or model instance specifying match rules.
        """
        self._operations.append(
            (
                "delete",
                {
                    "collection_name": collection_name,
                    "filter": filter_,
                },
            )
        )

    async def commit(self) -> None:
        """Flush queued operations to Qdrant. Called automatically by dependency."""
        if not self._operations:
            return

        # 延迟初始化 client，提升测试便利性
        if self._client is None:
            self._client = get_qdrant_client()

        # 简单串行执行；如需高并发可在此优化
        for op_name, params in self._operations:
            if op_name == "upsert":
                # QdrantClient.upsert is synchronous; call directly inside async context
                self._client.upsert(collection_name=params["collection_name"], points=params["points"])
            elif op_name == "delete":
                # Delete points matching filter
                self._client.delete(collection_name=params["collection_name"], points_selector=params["filter"]) # pass filter as points_selector
            # 未来可以在这里支持更多操作，如 delete, search 等

        # 清理已执行操作
        self._operations.clear()

    async def rollback(self) -> None:
        """Discard all queued operations. Placeholder for API symmetry."""
        self._operations.clear()

    async def close(self) -> None:  # noqa: D401
        """No-op for now. Reserved for future resource cleanup."""
        self._operations.clear()

    # --------------------- context manager helpers --------------------

    async def __aenter__(self) -> "VectorSession":  # type: ignore[name-defined]
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()


# ---------------------------------------------------------------------
# FastAPI dependency helper
# ---------------------------------------------------------------------

async def get_vector_session() -> AsyncGenerator[VectorSession, None]:
    """
    Dependency that yields a new `VectorSession` per request. On successful
    completion, queued operations are flushed to Qdrant; otherwise they are
    discarded.

    FastAPI 依存性(いぞんせい)です。リクエストごとに新(あたら)しい `VectorSession` を返(かえ)します。
    処理(しょり)が成功(せいこう)すれば commit、失敗(しっぱい)すれば rollback します。
    """
    session = VectorSession()
    try:
        yield session
        # 如果执行到这里说明业务逻辑未抛出异常
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

