"""Provide a globally injected aioredis client.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
import redis.asyncio as redis

_client: Optional[redis.Redis] = None

# ------------------------------------------------------------------
# Setter / Getter
# ------------------------------------------------------------------

def set_redis_client(client: redis.Redis) -> None:
    global _client
    _client = client

def get_redis_client() -> redis.Redis:
    if _client is None:
        raise RuntimeError(
            "Redis client not set"
        )
    return _client

# ------------------------------------------------------------------
# Factory helper
# ------------------------------------------------------------------

def make_redis_client(url: str | None = None, **kwargs) -> redis.Redis:

    load_dotenv()

    if url is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    client: redis.Redis = redis.from_url(url, decode_responses=True, **kwargs)
    set_redis_client(client)
    return client 