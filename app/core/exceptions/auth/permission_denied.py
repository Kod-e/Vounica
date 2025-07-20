from typing import Optional

from .base import AuthException
from ..types import ErrorType

"""Permission denied (401)."""

class PermissionDeniedException(AuthException):
    """Raised when user lacks sufficient permissions to perform an action."""

    def __init__(self, message: str = "Permission denied", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.PERMISSION_DENIED, detail=detail) 