"""
OpenAI function-call tools for querying Vocab **based on UnitOfWork**.

改写为依赖 ``UnitOfWork``，复用请求级别数据库/向量会话与 ``user_id``，避免在工具内部
私自创建 session，提升一致性与安全性。
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



FUNCTION_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "search_by_name_regex",
        "description": "Search vocab by name using case-insensitive regex (current user scope)",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Case-insensitive regex pattern"},
                "limit": {
                    "type": "integer",
                    "description": "Max number of records (default 20)",
                    "default": 20,
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "search_by_usage_regex",
        "description": "Search vocab usage via regex (current user scope)",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern"},
                "limit": {
                    "type": "integer",
                    "description": "Max number of records (default 20)",
                    "default": 20,
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "search_by_usage_vector",
        "description": "Vector similarity search on vocab usage (current user scope)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query text"},
                "limit": {
                    "type": "integer",
                    "description": "Top-k (default 20)",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
]


def make_dispatch(uow: UnitOfWork) -> Dict[str, Callable[..., Coroutine[Any, Any, Any]]]:
    """Return function-name → coroutine mapping bound to given ``uow``.

    FastAPI handler can call::

        dispatch = make_dispatch(uow)
        result = await dispatch[name](**args)
    """

    return {
        "search_by_name_regex": lambda **kw: search_by_name_regex(uow, **kw),
        "search_by_usage_regex": lambda **kw: search_by_usage_regex(uow, **kw),
        "search_by_usage_vector": lambda **kw: search_by_usage_vector(uow, **kw),
    }


# Re-export
__all__ = [
    "FUNCTION_SCHEMAS",
    "make_dispatch",
    "search_by_name_regex",
    "search_by_usage_regex",
    "search_by_usage_vector",
]
