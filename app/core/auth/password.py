import warnings
from passlib.context import CryptContext

# 临时解决方案：屏蔽 bcrypt 版本检查警告
# 这是因为 bcrypt 4.1.1+ 版本移除了 __about__ 属性，但 passlib 1.7.4 仍然尝试访问它
# 根据 GitHub 问题 https://github.com/pyca/bcrypt/issues/684，这是一个已知问题
# 此警告不影响功能，但会在日志中产生噪音
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return _pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    return _pwd_ctx.verify(plain, hashed) 