"""
Server-side (5xx) exceptions.

サーバーエラー(5xx)に関(かん)する例外(れいがい)をまとめます。
"""
from .internal_error import InternalErrorException

__all__ = [
    "InternalErrorException",
] 