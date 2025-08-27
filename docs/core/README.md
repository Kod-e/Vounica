
# Core レイヤー README

Core レイヤーは、このプロジェクトの **一番下の基盤** です。 
Database Session, JWT, Redis, Qdrant client, Exception をここでまとめます。 
上の Infra / Service / API レイヤーは、この Core を使って動きます。

---

## Core の役割

Core は「共通の部品（toolbox）」を提供します。

- **DB**: SQLAlchemy の AsyncSession を安全に管理
- **JWT**: 認証用 Token の作成・検証
- **Redis**: Quota / Cache 用の client 提供
- **Qdrant**: Vector DB client と簡易トランザクション風の仕組み
- **Exception**: 共通の Error 型（JSON で統一）

Core が壊れると、上位レイヤーは全部動きません。最も重要な土台です。

---

## Database (PostgreSQL + SQLAlchemy)

DB は PostgreSQL を前提にしています。SQLAlchemy の **AsyncSession** を使い、
1 リクエスト = 1 セッションのライフサイクルで運用します。

```python
# app/core/db/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

- `commit()` : 成功したら保存
- `rollback()` : 例外時は取り消し
- `close()` : 最後に必ず閉じる

これで、毎回のリクエストが **安全** に DB を使えます。

---

## JWT (Authentication)

User 認証は **JWT** を使います。秘密鍵は `.env` から読み込みます。
- **本番**: ES256 (ECDSA P-256) + Base64 エンコードされた PEM を推奨
- **テスト**: HS256 + シンプルな固定 key（開発用）

```python
# app/core/auth/jwt.py（抜粋）
from datetime import datetime, timedelta

def create_access_token(user_id: int, *, expires_delta: timedelta | None = None) -> str:
    now = datetime.now()
    expire = now + (expires_delta or timedelta(minutes=EXPIRE_MINUTES))
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm=ALGORITHM)
```

Payload は **最小**：`sub` / `iat` / `exp` のみ。攻撃面を減らし、検証も速いです。

---

## Redis (Quota / Cache)

Redis は per-user の **Token quota** と簡単な **Cache** に使います。client は 1 回だけ作って再利用します。

```python
# app/core/redis/provider.py（抜粋）
import redis.asyncio as redis

def make_redis_client(url: str | None = None) -> redis.Redis:
    if url is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    client: redis.Redis = redis.from_url(url, decode_responses=True)
    set_redis_client(client)
    return client
```

どこからでも `get_redis_client()` で取得できます。

---

## Qdrant (Vector DB) と VectorSession

Qdrant はベクトル検索のための **Vector Database** です。語彙・文法・間違い・記憶・ストーリーなど、
テキストの意味検索に使います。ただし Qdrant は **transaction がありません**。そのため、
SQL と Qdrant がずれる危険があります。

Core では **VectorSession** という薄いラッパーを作り、
- request 成功 → ためた upsert/delete を **commit**
- request 失敗 → ためた操作を **rollback**（破棄）

とすることで **一貫性** を保ちます。

```python
# app/core/vector/session.py（抜粋）
class VectorSession:
    def __init__(self):
        self._operations: List[Tuple[str, Dict[str, Any]]] = []
        self._client = None

    def add_point(self, collection_name: str, point: Dict[str, Any]) -> None:
        self._operations.append(("upsert", {"collection_name": collection_name, "points": [point]}))

    def delete_by_ids(self, collection_name: str, ids: list[int]) -> None:
        self._operations.append(("delete", {"collection_name": collection_name, "ids": ids}))

    async def commit(self) -> None:
        if not self._client:
            self._client = get_qdrant_client()
        for op, params in self._operations:
            if op == "upsert":
                self._client.upsert(collection_name=params["collection_name"], points=params["points"])
            elif op == "delete":
                self._client.delete(collection_name=params["collection_name"], points_selector=params["ids"]) 
        self._operations.clear()
```

Embedding には OpenAI `text-embedding-3-small`（1536 dim）を使用しています。

---

## Exception Handling（共通エラー形式）

API のエラーは **同じ JSON 形式** に統一します。
`BaseException` を親にして、401/404/500 などを継承で表現します。

```python
# app/core/exceptions/base.py（抜粋）
class BaseException(Exception):
    def __init__(self, *, code: int, message: str, error_type: ErrorType, detail: dict | None = None):
        self.code = code
        self.message = message
        self.error_type = error_type
        self.detail = detail or {}

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "error_type": self.error_type.value,
            "detail": self.detail,
        }
```

例：
- `UnauthorizedException` (401)
- `NotFoundException` (404)
- `DatabaseException` (500)

フロントエンドはこの JSON を見て、安定して UI を出し分けできます。

---

## Password Hash（補足）

`passlib` + `bcrypt` で password を hash/verify します。bcrypt の warning は無視設定しています（機能に影響なし）。

```python
# app/core/auth/password.py（抜粋）
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)
```

---

## まとめ

Core は **最小で強い基盤** を提供します。

- DB: 例外安全な AsyncSession ライフサイクル
- JWT: 最小 payload の token（セキュア & 速い）
- Redis: per-user quota / cache
- Qdrant: VectorSession で SQL と一貫性
- Exception: 統一 JSON で安定したエラーハンドリング

ユーザーからは見えない部分ですが、プロダクトの安定性を守る大事な層です。