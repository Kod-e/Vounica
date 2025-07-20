from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Memory entry not found."""

class MemoryNotFoundException(NotFoundException):
    """Raised when a memory record is not found."""

    def __init__(self, message: str = "Memory not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.MEMORY_NOT_FOUND, detail=detail) 