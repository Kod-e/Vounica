from enum import Enum

"""
Type definitions for application-wide error codes.

Application全体(ぜんたい)で使用(しよう)するエラー種別(しゅべつ)を定義(ていぎ)します。
"""

class ErrorType(str, Enum):
    """Common error categories used throughout the application."""

    USER_NOT_FOUND = "user_not_found"
    UNAUTHORIZED = "unauthorized"
    INVALID_TOKEN = "invalid_token"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_NOT_FOUND = "resource_not_found"
    INTERNAL_ERROR = "internal_error" 