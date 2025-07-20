from typing import Optional

from .base import AuthException
from ..types import ErrorType

"""Invalid authentication token (401)."""

class InvalidTokenException(AuthException):
    """Raised when provided authentication token is invalid or expired."""

    def __init__(self, message: str = "Invalid token", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.INVALID_TOKEN, detail=detail) 