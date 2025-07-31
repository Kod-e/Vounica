from __future__ import annotations

import uuid
from datetime import datetime,timezone
from typing import Any, Dict, Sequence

from app.core.vector.embeddings import get_embedding
from app.core.vector.payload import VectorPayload
from app.core.vector.provider import get_qdrant_client
from app.core.vector.session import VectorSession

from .collections import COLLECTIONS_CONFIG, MODEL_FIELD_TO_COLLECTION, VectorCollection



# 创建Qdrant collection
def ensure_collections_exist() -> None:
    """Create all defined Qdrant collections if they are missing."""
    client = get_qdrant_client()
    for collection, params in COLLECTIONS_CONFIG.items():
        name = collection.value
        if not client.collection_exists(name):
            client.create_collection(collection_name=name, vectors_config=params)


# 构建Qdrant point
def _build_point(vector: Sequence[float], payload_extra: Dict[str, Any], origin_id: int) -> Dict[str, Any]:
    """Internal helper to build a Qdrant point dict."""
    base_payload = VectorPayload(
        user_id=payload_extra["user_id"],
        created_at=int(datetime.now().timestamp()),
    ).model_dump(mode="json")
    # 合并additional payload data
    payload = base_payload | payload_extra  # type: ignore[operator]
    return {
        "id": origin_id,
        "vector": vector,
        "payload": payload,
    }


# 将ORM实例中的可向量化字段进行向量化x
def queue_vector_from_instance(
    instance: Any,
    session: VectorSession,
) -> None:
    """Scan the given ORM instance and queue vector operations for all mappable fields.

    This will automatically look up the mapping in ``MODEL_FIELD_TO_COLLECTION`` and
    call the OpenAI embedding API for each matched field.

    Args:
        instance: SQLAlchemy ORM instance containing text fields.
        session: Active ``VectorSession`` used to queue operations.
    """
    model_name = instance.__class__.__name__

    # 遍历MODEL_FIELD_TO_COLLECTION中的映射关系, 将ORM实例中的可向量化字段进行向量化
    for (mapped_model, field_name), collection in MODEL_FIELD_TO_COLLECTION.items():
        if mapped_model != model_name:
            continue

        text_value = getattr(instance, field_name, None)
        if not text_value:
            # 跳过空值或缺失值
            continue

        # 获取embedding(OpenAI API)
        vector = get_embedding(str(text_value))
        origin_id = getattr(instance, "id", None)
        if origin_id is None:
            raise ValueError("origin_id is None")
        # 构建payload和point
        payload_extra = {
            "user_id": getattr(instance, "user_id", 0),  # 如果user_id不存在, 则使用0
            "model": model_name,
            "field": field_name,
            "origin_id": origin_id,
        }
        point = _build_point(vector, payload_extra, origin_id)

        # 将point添加到vector session中
        session.add_point(collection.value, point)
# --------------------------------------------------------------
# 删除操作: 从 Qdrant 中删除与 ORM 实例关联的全部向量
# --------------------------------------------------------------


def queue_vector_delete_for_instance(
    instance: Any,
    session: VectorSession,
) -> None:
    """Queue deletion of all vector points associated with the given ORM instance.

    根据 ``MODEL_FIELD_TO_COLLECTION`` 的映射，通过 `origin_id` 来删除。
    """

    model_name = instance.__class__.__name__
    origin_id = getattr(instance, "id", None)
    if origin_id is None:
        return

    for (mapped_model, _field_name), collection in MODEL_FIELD_TO_COLLECTION.items():
        if mapped_model != model_name:
            continue

        session.delete_by_ids(collection.value, [origin_id]) 