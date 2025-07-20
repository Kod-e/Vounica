from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""User entity not found."""

class UserNotFoundException(NotFoundException):
    """Raised when a user cannot be located."""

    def __init__(self, message: str = "User not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.USER_NOT_FOUND, detail=detail) 