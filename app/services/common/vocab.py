"""Vocab service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.vocab import Vocab
from app.infra.repo.vocab_repository import VocabRepository
from app.infra.uow import UnitOfWork


class VocabService(BaseService[Vocab]):
    """Service for Vocab entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._repo : VocabRepository = VocabRepository(db=uow.db)
        super().__init__(self._repo)

__all__ = ["VocabService"] 