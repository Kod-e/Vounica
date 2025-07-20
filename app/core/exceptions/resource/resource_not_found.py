from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Generic resource not found exception."""

class ResourceNotFoundException(NotFoundException):
    """Raised when a requested resource is missing."""

    def __init__(self, message: str = "Resource not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.RESOURCE_NOT_FOUND, detail=detail) 