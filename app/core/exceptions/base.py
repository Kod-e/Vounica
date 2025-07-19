"""
Base exceptions and error type handling.

Application共通(きょうつう)の例外(れいがい)を定義(ていぎ)します。
"""
from typing import Optional
from .types import ErrorType

# 主异常类
class BaseException(Exception):
    def __init__(self, *, code: str, message: str, error_type: ErrorType, detail: Optional[dict] = None):
        self.code = code
        self.message = message
        self.error_type = error_type
        self.detail = detail or {}

    def __str__(self):
        return f"{self.__class__.__name__}(code={self.code}, message={self.message}, error_type={self.error_type}, detail={self.detail})"
    
    # 在需要json返回时
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "error_type": self.error_type.value,
            "detail": self.detail,
        }