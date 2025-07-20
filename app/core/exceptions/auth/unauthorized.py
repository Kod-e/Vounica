from typing import Optional

from .base import AuthException
from ..types import ErrorType

"""Unauthorized request (401)."""

class UnauthorizedException(AuthException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Unauthorized", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.UNAUTHORIZED, detail=detail) 