from typing import Optional

from ..common.not_found import NotFoundException
from ..types import ErrorType

"""Story not found in the system."""

class StoryNotFoundException(NotFoundException):
    """Raised when a story entity is not found."""

    def __init__(self, message: str = "Story not found", detail: Optional[dict] = None):
        super().__init__(message=message, error_type=ErrorType.STORY_NOT_FOUND, detail=detail) 