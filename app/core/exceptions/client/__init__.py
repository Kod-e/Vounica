"""
Client-related (4xx) exceptions.

クライアントエラー(4xx)に関(かん)する例外(れいがい)をまとめます。
"""
from .user_not_found import UserNotFoundException
from .resource_not_found import ResourceNotFoundException

__all__ = [
    "UserNotFoundException",
    "ResourceNotFoundException",
] 