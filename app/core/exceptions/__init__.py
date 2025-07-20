"""
Public interfaces for exception handling.

Application共通(きょうつう)の例外(れいがい)をまとめて公開(こうかい)します。
"""
from .base import BaseException
from .types import ErrorType

# Auth 401
from .auth import AuthException, UnauthorizedException, InvalidTokenException, PermissionDeniedException
# Resource 404
from .common import NotFoundException
from .resource import UserNotFoundException, ResourceNotFoundException
# Server 500
from .server import InternalErrorException

__all__ = [
    "BaseException",
    "ErrorType",
    # auth
    "AuthException",
    "UnauthorizedException",
    "InvalidTokenException",
    "PermissionDeniedException",
    # common / resource
    "NotFoundException",
    "UserNotFoundException",
    "ResourceNotFoundException",
    # server
    "InternalErrorException",
] 