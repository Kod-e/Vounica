"""
Public interfaces for exception handling.

Application共通(きょうつう)の例外(れいがい)をまとめて公開(こうかい)します。
"""
from .base import BaseException
from .types import ErrorType

# Auth 401
from .auth import UnauthorizedException, InvalidTokenException, PermissionDeniedException
# Client 404
from .client import UserNotFoundException, ResourceNotFoundException
# Server 500
from .server import InternalErrorException

__all__ = [
    "BaseException",
    "ErrorType",
    # auth
    "UnauthorizedException",
    "InvalidTokenException",
    "PermissionDeniedException",
    # client
    "UserNotFoundException",
    "ResourceNotFoundException",
    # server
    "InternalErrorException",
] 