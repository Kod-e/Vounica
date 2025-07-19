from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""
Resource not found exception.

リソースが見つからない場合(ばあい)に使用(しよう)します。
"""

class ResourceNotFoundException(BaseException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found", detail: Optional[dict] = None):
        super().__init__(code="404", message=message, error_type=ErrorType.RESOURCE_NOT_FOUND, detail=detail) 