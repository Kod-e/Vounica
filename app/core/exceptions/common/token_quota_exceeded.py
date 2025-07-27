from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Token quota exceeded exception."""

class TokenQuotaExceededException(BaseException):
    """Raised when user exceeds token quota."""

    def __init__(self, message: str = "Token quota exceeded", detail: Optional[dict] = None):
        super().__init__(code=429, message=message, error_type=ErrorType.TOKEN_QUOTA_EXCEEDED, detail=detail) 