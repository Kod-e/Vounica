"""
Redis connectivity and quota bucket diagnostic tool.

ローカル Redis 接続(せつぞく)と配額(はいがく)バケット確認(かくにん)ツール。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from types import SimpleNamespace
from typing import Optional

from dotenv import load_dotenv

# 尽量使用项目内的 provider，保证与应用一致
try:
    from app.core.redis.provider import make_redis_client
    from app.infra.quota.bucket import QuotaBucket
except Exception as exc:  # noqa: BLE001
    print(f"[fatal] failed to import project modules: {exc}")
    sys.exit(1)


async def check_redis(url: Optional[str]) -> bool:
    # 打印 REDIS_URL 生效值
    effective = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"[info] REDIS_URL = {effective}")

    # 构造客户端并 ping
    client = make_redis_client(url=effective)
    try:
        pong = await client.ping()
        print(f"[ok] ping => {pong}")

        # 简单 set/get 验证
        key = f"healthcheck:test:{int(time.time())}"
        await client.set(key, "1", ex=60)
        got = await client.get(key)
        print(f"[ok] set/get => key={key} value={got}")
        return True
    finally:
        # 关闭连接
        try:
            await client.aclose()
        except Exception:
            pass


async def check_quota(url: Optional[str], user_id: int, token_quota: float, need: int, consume: int, multiplier: int) -> None:
    # 使用与应用一致的客户端
    client = make_redis_client(url=url or os.getenv("REDIS_URL"))
    try:
        # 仅需 id 与 token_quota 字段
        user = SimpleNamespace(id=user_id, token_quota=token_quota)
        bucket = QuotaBucket(client, user)

        # 先检查余额
        try:
            await bucket.check(need=need)
            print(f"[ok] quota.check need={need} => OK")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] quota.check need={need} => {exc}")

        # 可选消费再查看余额
        if consume > 0:
            await bucket.consume(used=consume, multiplier=multiplier)
            print(f"[ok] quota.consume used={consume} multiplier={multiplier} => OK")

        # 读取剩余（调试：访问内部方法以便打印）
        remaining = await bucket._get_remaining(create_if_missing=True)  # noqa: SLF001
        print(f"[info] quota.remaining => {remaining}")
    finally:
        try:
            await client.aclose()
        except Exception:
            pass


async def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Redis and quota diagnostics")
    parser.add_argument("--url", default=None, help="Override REDIS_URL for this run")
    parser.add_argument("--loop", action="store_true", help="Run continuously until Ctrl+C")
    parser.add_argument("--interval", type=int, default=5, help="Loop interval seconds")

    # quota 相关
    parser.add_argument("--with-bucket", action="store_true", help="Also check QuotaBucket behavior")
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--token-quota", type=float, default=float(os.getenv("TEST_TOKEN_QUOTA", 1000)))
    parser.add_argument("--need", type=int, default=0, help="Need tokens for quota.check")
    parser.add_argument("--consume", type=int, default=0, help="Tokens to consume after check")
    parser.add_argument("--multiplier", type=int, default=1, help="Cost multiplier for consume")

    args = parser.parse_args()

    async def run_once() -> None:
        ok = await check_redis(args.url)
        if not ok:
            print("[error] redis connectivity check failed")
        if args.with_bucket:
            await check_quota(args.url, args.user_id, args.token_quota, args.need, args.consume, args.multiplier)

    if not args.loop:
        await run_once()
        return

    print("[info] start loop mode; press Ctrl+C to stop")
    while True:
        try:
            await run_once()
        except KeyboardInterrupt:
            break
        except Exception as exc:  # noqa: BLE001
            print(f"[error] unexpected error: {exc}")
        await asyncio.sleep(args.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
