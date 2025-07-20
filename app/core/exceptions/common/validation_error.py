from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""422 validation error."""

class ValidationException(BaseException):
    """Raised when payload validation fails."""

    def __init__(self, message: str = "Validation error", detail: Optional[dict] = None):
        super().__init__(code=422, message=message, error_type=ErrorType.VALIDATION_ERROR, detail=detail) 