from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Generic 404 Not Found exception base class."""

class NotFoundException(BaseException):
    """Base class for all 404 not-found errors."""

    def __init__(self, *, message: str = "Resource not found", error_type: ErrorType = ErrorType.RESOURCE_NOT_FOUND, detail: Optional[dict] = None):
        super().__init__(code=404, message=message, error_type=error_type, detail=detail) 