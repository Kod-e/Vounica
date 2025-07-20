from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Grammar rule not found."""

class GrammarNotFoundException(NotFoundException):
    """Raised when a grammar rule is not found."""

    def __init__(self, message: str = "Grammar not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.GRAMMAR_NOT_FOUND, detail=detail) 