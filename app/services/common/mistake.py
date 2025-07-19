"""Mistake service wrapper.

Mistakeモデル用 CRUD + ベクター同期 Service
"""

from app.services.common.common_base import BaseService
from app.infra.models.mistake import Mistake
from app.infra.repo.mistake_repository import MistakeRepository


class MistakeService(BaseService[Mistake]):
    """Service for Mistake entity."""

    def __init__(self):
        super().__init__(MistakeRepository())

__all__ = ["MistakeService"] 