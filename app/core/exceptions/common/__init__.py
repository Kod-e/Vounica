"""
Common base exceptions that can be inherited by domain-specific errors.
"""
from .not_found import NotFoundException
from .bad_request import BadRequestException
from .validation_error import ValidationException
from .token_quota_exceeded import TokenQuotaExceededException

__all__ = [
    "NotFoundException",
    "BadRequestException",
    "ValidationException",
    "TokenQuotaExceededException",
] 