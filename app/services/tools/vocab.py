"""
OpenAI function-call tools for querying Vocab **based on UnitOfWork**.
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine

from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.infra.models.vocab import Vocab
from app.core.vector.embeddings import get_embedding
from app.core.vector.provider import get_qdrant_client
from app.infra.vector.collections import VectorCollection

# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _to_dict(record: Vocab) -> Dict[str, Any]:
    """Convert ORM record to plain dict for JSON serialization."""
    return {
        "id": record.id,
        "user_id": record.user_id,
        "name": record.name,
        "usage": record.usage,
        "status": record.status,
    }


# ---------------------------------------------------------------------------
# Query functions – all require ``uow`` and leverage its db / user_id
# ---------------------------------------------------------------------------


async def search_by_name_regex(
    uow: UnitOfWork,
    *,
    pattern: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Search ``Vocab.name`` via SQL ILIKE bound to current user."""

    regex = f"%{pattern}%"

    stmt = select(Vocab).where(
        Vocab.user_id == uow.user_id,
        Vocab.name.ilike(regex),
    ).limit(limit)

    result = await uow.db.execute(stmt)
    records = result.scalars().all()
    return [_to_dict(r) for r in records]


async def search_by_usage_regex(
    uow: UnitOfWork,
    *,
    pattern: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Search ``Vocab.usage`` via SQL ILIKE bound to current user."""

    regex = f"%{pattern}%"
    stmt = select(Vocab).where(
        Vocab.user_id == uow.user_id,
        Vocab.usage.ilike(regex),
    ).limit(limit)

    result = await uow.db.execute(stmt)
    records = result.scalars().all()
    return [_to_dict(r) for r in records]


async def search_by_usage_vector(
    uow: UnitOfWork,
    *,
    query: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Vector similarity search on ``usage`` field (current user scope)."""

    embedding = get_embedding(query)
    client = get_qdrant_client()

    q_filter = {
        "must": [
            {"key": "user_id", "match": {"value": uow.user_id}},
        ]
    }

    points = client.search(
        collection_name=VectorCollection.VOCAB_USAGE.value,
        query_vector=embedding,
        limit=limit,
        query_filter=q_filter,
    )

    origin_ids = [p.payload.get("origin_id") for p in points if p.payload.get("origin_id")]
    if not origin_ids:
        return []

    # 保证返回顺序与相似度一致
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}

    stmt = select(Vocab).where(Vocab.id.in_(origin_ids))
    result = await uow.db.execute(stmt)
    records = result.scalars().all()
    return sorted([_to_dict(r) for r in records], key=lambda r: order_map.get(r["id"], 9999))


__all__ = [
    "search_by_name_regex",
    "search_by_usage_regex",
    "search_by_usage_vector",
]
