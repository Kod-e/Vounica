"""
Base exception and serialization helpers for the application.
"""
from typing import Optional
from .types import ErrorType

# primary exception class
class BaseException(Exception):
    def __init__(self, *, code: int, message: str, error_type: ErrorType, detail: Optional[dict] = None):
        self.code = code
        self.message = message
        self.error_type = error_type
        self.detail = detail or {}

    def __str__(self):
        return f"{self.__class__.__name__}(code={self.code}, message={self.message}, error_type={self.error_type}, detail={self.detail})"
    
    # dict for JSON responses
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "error_type": self.error_type.value,
            "detail": self.detail,
        }