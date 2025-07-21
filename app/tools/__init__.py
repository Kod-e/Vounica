from __future__ import annotations

import json
from typing import Any, Dict, List

from app.services.common.search import ResourceType, search
from app.core.uow import UnitOfWork


async def search_resources(
    uow: UnitOfWork,
    *,
    resource: str,
    user_id: int,
    language: str | None = None,
    category: str | None = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """工具：根据过滤条件搜索资源并返回 dict 列表。"""
    res_type = ResourceType(resource)
    results = await search(
        uow,
        res_type,
        user_id=user_id,
        language=language,
        category=category,
        limit=limit,
    )
    return [r.model_dump(mode="json") for r in results]  # type: ignore[attr-defined]


FUNCTION_SCHEMAS = [
    {
        "name": "search_resources",
        "description": "Search user resources with optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "resource": {
                    "type": "string",
                    "enum": [e.value for e in ResourceType],
                    "description": "Resource type to search",
                },
                "user_id": {"type": "integer"},
                "language": {"type": "string"},
                "category": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["resource", "user_id"],
        },
    }
]

DISPATCH = {
    "search_resources": search_resources,
}

__all__ = ["FUNCTION_SCHEMAS", "DISPATCH", "search_resources"] 