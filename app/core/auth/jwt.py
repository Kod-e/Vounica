from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from app.core.exceptions.auth.invalid_token import InvalidTokenException
from dotenv import load_dotenv
import os

load_dotenv()

# 使用 ES256 (ECDSA) 进行签名 / 验证
_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")
if not _PRIVATE_KEY or not _PUBLIC_KEY:
    raise RuntimeError("JWT_PRIVATE_KEY / JWT_PUBLIC_KEY must be set in .env")

ALGORITHM = "ES256"
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def create_access_token(user_id: int, *, expires_delta: timedelta | None = None) -> str:
    """生成 ES256 JWT。

    仅包含 sub / iat / exp 三个字段，保持最小化。
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=EXPIRE_MINUTES))
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Dict[str, Any]:
    """校验 token 并返回 payload。

    Raises:
        JWTError: token 无效或过期。
    """
    try:
        payload = jwt.decode(token, _PUBLIC_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise InvalidTokenException() from exc 