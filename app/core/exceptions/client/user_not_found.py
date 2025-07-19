from typing import Optional

from ..base import BaseException
from ..types import ErrorType

"""
User not found exception.

userが存在(そんざい)しない場合(ばあい)に使用(しよう)します。
"""

class UserNotFoundException(BaseException):
    """Raised when user record cannot be located."""

    def __init__(self, message: str = "User not found", detail: Optional[dict] = None):
        super().__init__(code="404", message=message, error_type=ErrorType.USER_NOT_FOUND, detail=detail) 