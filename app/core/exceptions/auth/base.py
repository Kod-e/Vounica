from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Common base class for authentication related 401 errors."""

class AuthException(BaseException):
    """Base class for all 401 authentication errors."""

    def __init__(self, *, message: str = "Unauthorized", error_type: ErrorType = ErrorType.UNAUTHORIZED, detail: Optional[dict] = None):
        super().__init__(code=401, message=message, error_type=error_type, detail=detail) 