"""Mistake service wrapper.

Mistakeモデル用 CRUD + ベクター同期 Service
"""

from app.services.common.common_base import BaseService
from app.infra.models.mistake import Mistake
from app.infra.repo.mistake_repository import MistakeRepository
from app.infra.uow import UnitOfWork


class MistakeService(BaseService[Mistake]):
    """Service for Mistake entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._repo : MistakeRepository = MistakeRepository(db=uow.db)
        super().__init__(self._repo)

__all__ = ["MistakeService"] 