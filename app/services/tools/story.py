"""
OpenAI function-call tools for Story entity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Callable, Coroutine

from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.infra.models.story import Story
from app.core.vector.embeddings import get_embedding
from app.core.vector.provider import get_qdrant_client
from app.infra.vector.collections import VectorCollection


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------

def _to_dict(obj: Story) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "user_id": obj.user_id,
        "content": obj.content,
        "summary": obj.summary,
        "category": obj.category,
        "language": obj.language,
    }


# ------------------------------------------------------------------
# Regex helpers
# ------------------------------------------------------------------

async def search_story_content_regex(uow: UnitOfWork, *, pattern: str, limit: int = 20) -> List[Dict[str, Any]]:
    regex = f"%{pattern}%"
    stmt = select(Story).where(Story.user_id == uow.user_id, Story.content.ilike(regex)).limit(limit)
    res = await uow.db.execute(stmt)
    return [_to_dict(r) for r in res.scalars().all()]


async def search_story_summary_regex(uow: UnitOfWork, *, pattern: str, limit: int = 20) -> List[Dict[str, Any]]:
    regex = f"%{pattern}%"
    stmt = select(Story).where(Story.user_id == uow.user_id, Story.summary.ilike(regex)).limit(limit)
    res = await uow.db.execute(stmt)
    return [_to_dict(r) for r in res.scalars().all()]


async def search_story_category_regex(uow: UnitOfWork, *, pattern: str, limit: int = 20) -> List[Dict[str, Any]]:
    regex = f"%{pattern}%"
    stmt = select(Story).where(Story.user_id == uow.user_id, Story.category.ilike(regex)).limit(limit)
    res = await uow.db.execute(stmt)
    return [_to_dict(r) for r in res.scalars().all()]


# ------------------------------------------------------------------
# Vector helpers
# ------------------------------------------------------------------

async def _vector_search(
    uow: UnitOfWork,
    *,
    query: str,
    collection: VectorCollection,
    limit: int = 20,
) -> List[int]:
    embedding = get_embedding(query)
    client = get_qdrant_client()
    q_filter = {"must": [{"key": "user_id", "match": {"value": uow.user_id}}]}
    points = client.search(
        collection_name=collection.value,
        query_vector=embedding,
        limit=limit,
        query_filter=q_filter,
    )
    return [p.payload.get("origin_id") for p in points if p.payload.get("origin_id")]


async def search_story_content_vector(uow: UnitOfWork, *, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    origin_ids = await _vector_search(uow, query=query, collection=VectorCollection.STORY_CONTENT, limit=limit)
    if not origin_ids:
        return []
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}
    stmt = select(Story).where(Story.id.in_(origin_ids))
    res = await uow.db.execute(stmt)
    return sorted([_to_dict(r) for r in res.scalars().all()], key=lambda r: order_map.get(r["id"], 9999))


async def search_story_summary_vector(uow: UnitOfWork, *, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    origin_ids = await _vector_search(uow, query=query, collection=VectorCollection.STORY_SUMMARY, limit=limit)
    if not origin_ids:
        return []
    order_map = {oid: idx for idx, oid in enumerate(origin_ids)}
    stmt = select(Story).where(Story.id.in_(origin_ids))
    res = await uow.db.execute(stmt)
    return sorted([_to_dict(r) for r in res.scalars().all()], key=lambda r: order_map.get(r["id"], 9999))


# ------------------------------------------------------------------
# Schemas & dispatch
# ------------------------------------------------------------------

__all__ = [
    "search_story_content_regex",
    "search_story_summary_regex",
    "search_story_category_regex",
    "search_story_content_vector",
    "search_story_summary_vector",
] 