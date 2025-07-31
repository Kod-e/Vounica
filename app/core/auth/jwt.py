from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from app.core.exceptions.auth.invalid_token import InvalidTokenException
from dotenv import load_dotenv
import os

load_dotenv()

# 检测是否在测试环境中
IS_TEST = os.getenv("TEST_MODE", "false").lower() == "true"

# 为测试环境配置简单的密钥和算法
TEST_SECRET_KEY = "test_secret_key_for_testing_public"

# 获取JWT配置
if IS_TEST:
    # 测试环境使用HS256算法和简单密钥
    _PRIVATE_KEY = TEST_SECRET_KEY
    _PUBLIC_KEY = TEST_SECRET_KEY  # HS256使用相同密钥验证
    ALGORITHM = "HS256"
else:
    # 生产环境使用ES256和PEM密钥
    _PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
    _PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "ES256")

EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# 验证配置是否有效
if not IS_TEST and (not _PRIVATE_KEY or not _PUBLIC_KEY):
    raise RuntimeError("JWT_PRIVATE_KEY / JWT_PUBLIC_KEY must be set in .env")


def create_access_token(user_id: int, *, expires_delta: timedelta | None = None) -> str:
    """生成 JWT。

    仅包含 sub / iat / exp 三个字段，保持最小化。
    """
    now = datetime.now()
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