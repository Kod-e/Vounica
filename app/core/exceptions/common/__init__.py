"""
Common base exceptions that can be inherited by domain-specific errors.
"""
from .not_found import NotFoundException
from .bad_request import BadRequestException
from .validation_error import ValidationException

__all__ = [
    "NotFoundException",
    "BadRequestException",
    "ValidationException",
] 