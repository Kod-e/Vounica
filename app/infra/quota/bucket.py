"""Redis-backed token quota bucket scoped to a specific user.
"""

from __future__ import annotations

import os
from typing import Optional

import redis.asyncio as redis
from dotenv import load_dotenv

from app.core.exceptions.common.token_quota_exceeded import TokenQuotaExceededException
from app.infra.models.user import User

load_dotenv()
# 默认4小时
_DEFAULT_WINDOW = int(os.getenv("TOKEN_QUOTA_WINDOW", "14400"))  # 秒


class QuotaBucket:
    """Per-user quota bucket using Redis TTL to reset periodically."""

    KEY_TEMPLATE = "quota:{user_id}"

    def __init__(
        self,
        redis_client: redis.Redis,
        user: User,
        *,
        window: Optional[int] = None,
    ) -> None:
        self._redis = redis_client
        self.user = user
        # 使用整数 token 计费；user.token_quota 可为小数但此处统一向上取整
        self.limit: int = int(float(user.token_quota))
        self.window = window or _DEFAULT_WINDOW
        self._key = self.KEY_TEMPLATE.format(user_id=user.id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # 检查token是否足够
    async def check(self, need: int = 0) -> None:
        """Ensure quota has at least `need` tokens remaining."""
        remaining = await self._get_remaining(create_if_missing=True)
        if remaining < need:
            raise TokenQuotaExceededException(
                message="Token quota exceeded",
                detail={"remaining": remaining, "required": need},
            )

    # 消费token
    async def consume(self, used: int, *, multiplier: int = 1) -> None:
        """Deduct tokens multiplied by model cost factor.

        Args:
            used: base token count measured by cheapest model (e.g., embedding).
            multiplier: price factor relative to base cost (>=1).
        """
        if used <= 0 or multiplier <= 0:
            return
        cost = used * multiplier

        # Use pipeline to ensure atomicity
        tr = self._redis.pipeline()
        tr.exists(self._key)
        exists = (await tr.execute())[0]
        if not exists:
            # Initialize balance = limit - used with TTL
            await self._redis.set(self._key, self.limit - cost, ex=self.window)
        else:
            await self._redis.decrby(self._key, cost)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    # 获取剩余token
    async def _get_remaining(self, *, create_if_missing: bool) -> int:
        # 查询当前剩余 token；键若不存在说明配额已重置或从未使用
        value = await self._redis.get(self._key)

        # 键不存在: 初始化为满配额并设置 TTL
        if value is None:
            if not create_if_missing:
                return self.limit
            await self._redis.set(self._key, self.limit, ex=self.window)
            return self.limit

        # 键存在: 正常返回剩余量；若解析失败则重置
        try:
            return int(value)
        except (TypeError, ValueError):
            # 数据异常: 重置为满配额
            await self._redis.set(self._key, self.limit, ex=self.window)
            return self.limit 