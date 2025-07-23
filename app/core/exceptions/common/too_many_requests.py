from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""429 Too Many Requests exception."""

class TooManyRequestsException(BaseException):
    """Raised when user exceeds quota or rate limit."""

    def __init__(self, message: str = "Too many requests", detail: Optional[dict] = None):
        super().__init__(code=429, message=message, error_type=ErrorType.TOO_MANY_REQUESTS, detail=detail) 