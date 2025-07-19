from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""
Unauthorized exception.

認証(にんしょう)されていないリクエストに対(たい)して使用(しよう)します。
"""

class UnauthorizedException(BaseException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Unauthorized", detail: Optional[dict] = None):
        super().__init__(code="401", message=message, error_type=ErrorType.UNAUTHORIZED, detail=detail) 