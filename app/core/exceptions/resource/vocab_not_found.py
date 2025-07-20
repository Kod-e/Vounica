from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Vocabulary entry not found."""

class VocabNotFoundException(NotFoundException):
    """Raised when a vocabulary item is not found."""

    def __init__(self, message: str = "Vocabulary not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.VOCAB_NOT_FOUND, detail=detail) 