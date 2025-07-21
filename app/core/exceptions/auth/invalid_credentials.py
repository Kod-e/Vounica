from typing import Optional

from .base import AuthException
from ..types import ErrorType

"""Invalid email or password (401)."""

class InvalidCredentialsException(AuthException):
    """Raised when login credentials are incorrect."""

    def __init__(self, message: str = "Invalid credentials", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.INVALID_CREDENTIALS, detail=detail) 