"""
Unified search tool for all resources (vocab/grammar/mistake/story/memory).

LLM 只需一个函数 `search_resource` 即可完成所有正则/向量检索，
有效降低函数 schema 数量、节省 token，并提高模型选择正确参数的概率。
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine, Literal

from sqlalchemy import select

from app.infra.uow  import UnitOfWork
from app.infra.models import vocab as _vocab_model
from app.infra.models import grammar as _grammar_model
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
    "grammar",
    "mistake",
    "story",
    "memory",
]

_SEARCH_META: Dict[ResourceLiteral, Dict[str, Any]] = {
    "vocab": {
        "model": _vocab_model.Vocab,
        "fields": {
            "name": {"vector": True, "collection": VectorCollection.VOCAB_NAME},
            "usage": {"vector": True, "collection": VectorCollection.VOCAB_USAGE},
        },
    },
    "grammar": {
        "model": _grammar_model.Grammar,
        "fields": {
            "name": {"vector": True, "collection": VectorCollection.GRAMMAR_NAME},
            "usage": {"vector": True, "collection": VectorCollection.GRAMMAR_USAGE},
        },
    },
    "memory": {
        "model": _memory_model.Memory,
        "fields": {
            "content": {"vector": True, "collection": VectorCollection.MEMORY_CONTENT},
        },
    },
    "story": {
        "model": _story_model.Story,
        "fields": {
            "content": {"vector": True, "collection": VectorCollection.STORY_CONTENT},
            "summary": {"vector": True, "collection": VectorCollection.STORY_SUMMARY},
            "category": {"vector": True, "collection": VectorCollection.STORY_CATEGORY},
        },
    },
    "mistake": {
        "model": _mistake_model.Mistake,
        "fields": {
            "question": {"vector": True, "collection": VectorCollection.MISTAKE_QUESTION},
            "answer": {"vector": True, "collection": VectorCollection.MISTAKE_ANSWER},
            "correct_answer": {"vector": True, "collection": VectorCollection.MISTAKE_CORRECT_ANSWER},
            "error_reason": {"vector": True, "collection": VectorCollection.MISTAKE_ERROR_REASON},
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
    resource: ResourceLiteral,
    field: str,
    query: str,
    is_vector: bool = False,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Unified search across resources.

    Args:
        resource: Target entity name (enum).
        field:   Field name inside that entity.
        query:   Regex pattern or vector query text.
        is_vector:  "regex" (ILIKE) or "vector".
        limit:   Max rows.
    """
    # 检查是否是一个合法的查询
    # check if the resource is a valid query
    
    # 检查是否是一个合法的资源
    if resource not in _SEARCH_META:
        raise ValueError("Unsupported resource")
    
    # 检查是否是一个合法的字段
    meta = _SEARCH_META[resource]
    if field not in meta["fields"]:
        raise ValueError("Unsupported field for resource")

    # 检查是否是一个合法的查询方法
    field_cfg = meta["fields"][field]
    # 考虑到regex是默认的查询方法, 所以不需要检查
    # Regex is always supported; vector only when flag set.
    if is_vector and not field_cfg.get("vector", False):
        raise ValueError(f"{resource}.{field} does not support vector search")

    # 获取模型和字段
    Model = meta["model"]
    column = getattr(Model, field)

    # regex search
    if not is_vector:
        regex = f"%{query}%"
        stmt = select(Model).where(Model.user_id == uow.current_user.id, column.ilike(regex)).limit(limit)
        res = await uow.db.execute(stmt)
        return [_to_dict(r) for r in res.scalars().all()]

    # vector search
    collection: VectorCollection = field_cfg["collection"]
    embedding = get_embedding(query)
    client = get_qdrant_client()
    
    # 获取qdrant的client
    q_filter = {"must": [{"key": "user_id", "match": {"value": uow.current_user.id}}]}

    # 进行向量查询
    points = client.search(
        collection_name=collection.value,
        query_vector=embedding,
        limit=limit,
        query_filter=q_filter,
    )

    # 获取原始id
    origin_ids = [p.payload.get("origin_id") for p in points if p.payload.get("origin_id")]
    if not origin_ids:
        return []

    # 获取排序map
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}
    stmt = select(Model).where(Model.id.in_(origin_ids))

    # 执行查询
    res = await uow.db.execute(stmt)

    # 返回排序后的结果
    return sorted(
        # 将查询结果转换为字典
        [_to_dict(r) for r in res.scalars().all()],
        # 按向量检索返回的相似度排名排序
        key=lambda r: order_map.get(r["id"], len(order_map)),
    )


__all__ = ["search_resource", "ResourceLiteral"] 