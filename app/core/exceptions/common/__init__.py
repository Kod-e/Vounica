"""
Common base exceptions that can be inherited by domain-specific errors.
"""
from .not_found import NotFoundException

__all__ = [
    "NotFoundException",
] 