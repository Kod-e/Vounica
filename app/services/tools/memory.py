"""
OpenAI function-call tools for Memory entity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine

from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.infra.models.memory import Memory
from app.core.vector.embeddings import get_embedding
from app.core.vector.provider import get_qdrant_client
from app.infra.vector.collections import VectorCollection


# -------------------------------------------------------------
# Helper
# -------------------------------------------------------------

def _to_dict(obj: Memory) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "user_id": obj.user_id,
        "content": obj.content,
        "category": obj.category,
        "language": obj.language,
        "priority": obj.priority,
    }


# -------------------------------------------------------------
# Regex search
# -------------------------------------------------------------

async def search_memory_content_regex(
    uow: UnitOfWork,
    *,
    pattern: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    regex = f"%{pattern}%"
    stmt = select(Memory).where(
        Memory.user_id == uow.user_id,
        Memory.content.ilike(regex),
    ).limit(limit)
    res = await uow.db.execute(stmt)
    return [_to_dict(r) for r in res.scalars().all()]


# -------------------------------------------------------------
# Vector search
# -------------------------------------------------------------

async def search_memory_content_vector(
    uow: UnitOfWork,
    *,
    query: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    embedding = get_embedding(query)
    client = get_qdrant_client()
    q_filter = {"must": [{"key": "user_id", "match": {"value": uow.user_id}}]}
    points = client.search(
        collection_name=VectorCollection.MEMORY_CONTENT.value,
        query_vector=embedding,
        limit=limit,
        query_filter=q_filter,
    )
    origin_ids = [p.payload.get("origin_id") for p in points if p.payload.get("origin_id")]
    if not origin_ids:
        return []
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}
    stmt = select(Memory).where(Memory.id.in_(origin_ids))
    res = await uow.db.execute(stmt)
    return sorted([_to_dict(r) for r in res.scalars().all()], key=lambda r: order_map.get(r["id"], 9999))


# -------------------------------------------------------------
# Schemas & dispatch
# -------------------------------------------------------------

__all__ = [
    "search_memory_content_regex",
    "search_memory_content_vector",
] 