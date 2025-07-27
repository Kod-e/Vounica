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
_SEARCH_SCHEMA = {
    "name": "search_resource",
    "description": """ 
    检索用户在Vounica中记录的资源
    Vocab
    可以检索name和usage两个字段, 其中usage通过LLM生成, 表示了这个usage的使用场景
    return: 
    {
        "name": "单词",
        "usage": "单词的使用场景",
        "status": "单词的习得状态, 这是最近N次练习中, 单词被正确使用的概率, 从0-1"
    }
    
    
    Grammar
    可以检索name和usage两个字段, 其中usage通过LLM生成, 表示了这个usage的使用场景
    return: 
    {
        "name": "语法",
        "usage": "语法的使用场景",
        "status": "语法被正确使用的概率, 从0-1“
    }
    
    
    Memory
    Content: 记忆内容, 记忆内容需要可以被string化, 只能由LLM主动生成添加, 这里代表了你自己对这个用户的记忆
    return: 
    {
        "content": "记忆内容",
        "status": "记忆被正确使用的概率, 从0-1"
    }
    
    
    Story
    Content: 故事内容, 这里代表了用户自己记录的故事
    Summary: 故事概要, 这里代表了你阅读这个故事后对故事的总结, 只能由LLM主动生成添加
    return: 
    {
        "content": "故事内容",
        "summary": "故事概要",
        "category": "故事分类"
    }
    
    
    Mistake
    Question: 错误题目的内容
    Answer: 错题答案
    Correct_Answer: 正确答案
    Error_Reason: 错误原因, 只能由LLM根据回答主动生成添加
    return: 
    {
        "question": "错题题目",
        "question_type": "错题题目类型",
        "answer": "错题答案",
        "correct_answer": "正确答案",
        "error_reason": "错误原因"
    }
    
    资源/字段/方法对照：
    vocab.name → regex / vector
    vocab.usage → regex / vector
    grammar.name → regex / vector
    grammar.usage → regex / vector
    memory.content → regex / vector
    story.content → regex / vector
    story.summary → regex / vector
    story.category → regex / vector
    mistake.question → regex / vector
    mistake.answer → regex / vector
    mistake.correct_answer → regex / vector
    mistake.error_reason → regex / vector
    
    
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "resource": {
                "type": "string",
                "enum": ["vocab", "grammar", "mistake", "story", "memory"],
            },
            "field": {"type": "string"},
            "method": {"type": "string", "enum": ["regex", "vector"], "default": "regex"},
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 20},
        },
        "required": ["resource", "field", "query"],
    },
}

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
    if method == "vector" and not field_cfg.get("vector", False):
        raise ValueError(f"{resource}.{field} does not support vector search")

    # 获取模型和字段
    Model = meta["model"]
    column = getattr(Model, field)

    # regex search
    if method == "regex":
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