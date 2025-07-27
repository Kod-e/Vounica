"""
Public interfaces for exception handling.

Application共通(きょうつう)の例外(れいがい)をまとめて公開(こうかい)します。
"""
from .base import BaseException
from .types import ErrorType

# Auth 401
from .auth import AuthException, UnauthorizedException, InvalidTokenException, PermissionDeniedException
# Resource 404
from .common import NotFoundException, BadRequestException, ValidationException, TokenQuotaExceededException
from .resource import (
    UserNotFoundException,
    ResourceNotFoundException,
    StoryNotFoundException,
    VocabNotFoundException,
    GrammarNotFoundException,
    MistakeNotFoundException,
    MemoryNotFoundException,
)
# Server 500
from .server import InternalErrorException, DatabaseException

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
    "BadRequestException",
    "ValidationException",
    "UserNotFoundException",
    "ResourceNotFoundException",
    "StoryNotFoundException",
    "VocabNotFoundException",
    "GrammarNotFoundException",
    "MistakeNotFoundException",
    "MemoryNotFoundException",
    "TokenQuotaExceededException",
    # server
    "InternalErrorException",
    "DatabaseException",
] 