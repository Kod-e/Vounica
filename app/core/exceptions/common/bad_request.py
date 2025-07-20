from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Generic 400 bad request exception."""

class BadRequestException(BaseException):
    """Raised when a request is malformed or cannot be processed."""

    def __init__(self, message: str = "Bad request", detail: Optional[dict] = None):
        super().__init__(code=400, message=message, error_type=ErrorType.BAD_REQUEST, detail=detail) 