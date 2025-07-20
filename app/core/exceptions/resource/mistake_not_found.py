from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Mistake entry not found."""

class MistakeNotFoundException(NotFoundException):
    """Raised when a mistake record is not found."""

    def __init__(self, message: str = "Mistake not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.MISTAKE_NOT_FOUND, detail=detail) 