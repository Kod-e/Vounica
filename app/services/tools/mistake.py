"""
OpenAI function-call tools for Mistake entity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine, Literal

from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.infra.models.mistake import Mistake
from app.core.vector.embeddings import get_embedding
from app.core.vector.provider import get_qdrant_client
from app.infra.vector.collections import VectorCollection


_FIELD_TO_COLLECTION: Dict[str, VectorCollection] = {
    "question": VectorCollection.MISTAKE_QUESTION,
    "answer": VectorCollection.MISTAKE_ANSWER,
    "correct_answer": VectorCollection.MISTAKE_CORRECT_ANSWER,
    "error_reason": VectorCollection.MISTAKE_ERROR_REASON,
}

FieldLiteral = Literal["question", "answer", "correct_answer", "error_reason"]


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------

def _to_dict(obj: Mistake) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "user_id": obj.user_id,
        "question": obj.question,
        "answer": obj.answer,
        "correct_answer": obj.correct_answer,
        "error_reason": obj.error_reason,
        "question_type": obj.question_type,
        "language_type": obj.language_type,
    }


def _validate_field(field: str) -> VectorCollection:
    if field not in _FIELD_TO_COLLECTION:
        raise ValueError(f"Invalid field: {field}")
    return _FIELD_TO_COLLECTION[field]


# ------------------------------------------------------------------
# Regex search
# ------------------------------------------------------------------

async def search_mistake_regex(
    uow: UnitOfWork,
    *,
    field: FieldLiteral,
    pattern: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    column = getattr(Mistake, field)
    regex = f"%{pattern}%"
    stmt = select(Mistake).where(Mistake.user_id == uow.user_id, column.ilike(regex)).limit(limit)
    res = await uow.db.execute(stmt)
    return [_to_dict(r) for r in res.scalars().all()]


# ------------------------------------------------------------------
# Vector search
# ------------------------------------------------------------------

async def search_mistake_vector(
    uow: UnitOfWork,
    *,
    field: FieldLiteral,
    query: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    collection = _validate_field(field)
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
    stmt = select(Mistake).where(Mistake.id.in_(origin_ids))
    res = await uow.db.execute(stmt)
    return sorted([_to_dict(r) for r in res.scalars().all()], key=lambda r: order_map.get(r["id"], 9999))


# ------------------------------------------------------------------
# Schemas & dispatch
# ------------------------------------------------------------------

FIELD_ENUM = list(_FIELD_TO_COLLECTION.keys())

__all__ = [
    "search_mistake_regex",
    "search_mistake_vector",
] 