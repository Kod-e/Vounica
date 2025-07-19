from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""
Permission denied exception.

権限(けんげん)が不足(ふそく)している場合(ばあい)に使用(しよう)します。
"""

class PermissionDeniedException(BaseException):
    """Raised when user lacks sufficient permissions to perform an action."""

    def __init__(self, message: str = "Permission denied", detail: Optional[dict] = None):
        super().__init__(code="401", message=message, error_type=ErrorType.PERMISSION_DENIED, detail=detail) 