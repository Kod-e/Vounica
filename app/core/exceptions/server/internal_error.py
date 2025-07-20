from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Internal server error 500."""

class InternalErrorException(BaseException):
    """Raised when an unexpected server-side error occurs."""

    def __init__(self, message: str = "Internal server error", detail: Optional[dict] = None):
        super().__init__(code=500, message=message, error_type=ErrorType.INTERNAL_ERROR, detail=detail) 