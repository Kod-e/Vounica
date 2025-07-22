"""
Unified search tool for all resources (vocab/grammer/mistake/story/memory).

LLM 只需一个函数 `search_resource` 即可完成所有正则/向量检索，
有效降低函数 schema 数量、节省 token，并提高模型选择正确参数的概率。
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine, Literal

from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.infra.models import vocab as _vocab_model
from app.infra.models import grammer as _grammer_model
from app.infra.models import mistake as _mistake_model
from app.infra.models import story as _story_model
from app.infra.models import memory as _memory_model

from app.core.vector.embeddings import get_embedding
from app.core.vector.provider import get_qdrant_client
from app.infra.vector.collections import VectorCollection

# ------------------------------------------------------------------
# Resource meta-definition
# ------------------------------------------------------------------

ResourceLiteral = Literal[
    "vocab",
    "grammer",
    "mistake",
    "story",
    "memory",
]

_SEARCH_META: Dict[ResourceLiteral, Dict[str, Any]] = {
    "vocab": {
        "model": _vocab_model.Vocab,
        "fields": {
            "name": {"regex": True, "vector": False},
            "usage": {"regex": True, "vector": True, "collection": VectorCollection.VOCAB_USAGE},
        },
    },
    "grammer": {
        "model": _grammer_model.Grammar,
        "fields": {
            "name": {"regex": True, "vector": False},
            "usage": {"regex": True, "vector": True, "collection": VectorCollection.GRAMMER_USAGE},
        },
    },
    "memory": {
        "model": _memory_model.Memory,
        "fields": {
            "content": {"regex": True, "vector": True, "collection": VectorCollection.MEMORY_CONTENT},
        },
    },
    "story": {
        "model": _story_model.Story,
        "fields": {
            "content": {"regex": True, "vector": True, "collection": VectorCollection.STORY_CONTENT},
            "summary": {"regex": True, "vector": True, "collection": VectorCollection.STORY_SUMMARY},
            "category": {"regex": True, "vector": False},
        },
    },
    "mistake": {
        "model": _mistake_model.Mistake,
        "fields": {
            "question": {"regex": True, "vector": True, "collection": VectorCollection.MISTAKE_QUESTION},
            "answer": {"regex": True, "vector": True, "collection": VectorCollection.MISTAKE_ANSWER},
            "correct_answer": {"regex": True, "vector": True, "collection": VectorCollection.MISTAKE_CORRECT_ANSWER},
            "error_reason": {"regex": True, "vector": True, "collection": VectorCollection.MISTAKE_ERROR_REASON},
        },
    },
}

# ------------------------------------------------------------------
# Helper converter
# ------------------------------------------------------------------

def _to_dict(obj) -> Dict[str, Any]:  # noqa: ANN001
    """Convert SQLAlchemy model instance to dict by introspection."""
    # 简单序列化：返回可 json 化的字段
    return {
        c.key: getattr(obj, c.key)
        for c in obj.__table__.columns  # type: ignore[attr-defined]
    }


# ------------------------------------------------------------------
# Unified search implementation
# ------------------------------------------------------------------

async def search_resource(
    uow: UnitOfWork,
    *,
    resource: ResourceLiteral,
    field: str,
    query: str,
    method: Literal["regex", "vector"] = "regex",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Unified search across resources.

    Args:
        resource: Target entity name (enum).
        field:   Field name inside that entity.
        query:   Regex pattern or vector query text.
        method:  "regex" (ILIKE) or "vector".
        limit:   Max rows.
    """

    if resource not in _SEARCH_META:
        raise ValueError("Unsupported resource")

    meta = _SEARCH_META[resource]
    if field not in meta["fields"]:
        raise ValueError("Unsupported field for resource")

    field_cfg = meta["fields"][field]
    if not field_cfg.get(method, False):
        raise ValueError(f"Method {method} not supported on {resource}.{field}")

    Model = meta["model"]
    column = getattr(Model, field)

    if method == "regex":
        regex = f"%{query}%"
        stmt = select(Model).where(Model.user_id == uow.user_id, column.ilike(regex)).limit(limit)
        res = await uow.db.execute(stmt)
        return [_to_dict(r) for r in res.scalars().all()]

    # vector search
    collection: VectorCollection = field_cfg["collection"]
    embedding = get_embedding(query)
    client = get_qdrant_client()
    q_filter = {"must": [{"key": "user_id", "match": {"value": uow.user_id}}]}
    points = client.search(
        collection_name=collection.value,
        query_vector=embedding,
        limit=limit,
        query_filter=q_filter,
    )
    origin_ids = [p.payload.get("origin_id") for p in points if p.payload.get("origin_id")]
    if not origin_ids:
        return []
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}
    stmt = select(Model).where(Model.id.in_(origin_ids))
    res = await uow.db.execute(stmt)
    return sorted([_to_dict(r) for r in res.scalars().all()], key=lambda r: order_map.get(r["id"], 9999))


__all__ = ["search_resource", "ResourceLiteral"] 