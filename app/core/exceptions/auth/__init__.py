"""
Authentication-related exceptions.

認証(にんしょう)に関(かん)する例外(れいがい)をまとめます。
"""
from .unauthorized import UnauthorizedException
from .invalid_token import InvalidTokenException
from .permission_denied import PermissionDeniedException

__all__ = [
    "UnauthorizedException",
    "InvalidTokenException",
    "PermissionDeniedException",
] 