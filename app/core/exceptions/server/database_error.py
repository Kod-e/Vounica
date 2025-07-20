from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""Database operation error 500."""

class DatabaseException(BaseException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database error", detail: Optional[dict] = None):
        super().__init__(code=500, message=message, error_type=ErrorType.DATABASE_ERROR, detail=detail) 