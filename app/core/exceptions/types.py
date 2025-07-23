"""
Centralized enumeration of error types used throughout the application.
"""
from enum import Enum

class ErrorType(str, Enum):
    """Common error categories used throughout the application."""

    USER_NOT_FOUND = "user_not_found"
    UNAUTHORIZED = "unauthorized"
    INVALID_TOKEN = "invalid_token"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_NOT_FOUND = "resource_not_found"
    STORY_NOT_FOUND = "story_not_found"
    VOCAB_NOT_FOUND = "vocab_not_found"
    GRAMMAR_NOT_FOUND = "grammar_not_found"
    MISTAKE_NOT_FOUND = "mistake_not_found"
    MEMORY_NOT_FOUND = "memory_not_found"
    BAD_REQUEST = "bad_request"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"
    INTERNAL_ERROR = "internal_error"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOO_MANY_REQUESTS = "too_many_requests" 