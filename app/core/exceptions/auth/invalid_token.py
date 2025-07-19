from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""
Invalid token exception.

tokenが無効(むこう)な場合(ばあい)に使用(しよう)します。
"""

class InvalidTokenException(BaseException):
    """Raised when provided authentication token is invalid or expired."""

    def __init__(self, message: str = "Invalid token", detail: Optional[dict] = None):
        super().__init__(code="401", message=message, error_type=ErrorType.INVALID_TOKEN, detail=detail) 