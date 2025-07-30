"""Vocab service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.vocab import Vocab
from app.infra.repo.vocab_repository import VocabRepository
from app.infra.context import uow_ctx


class VocabService(BaseService[Vocab]):
    """Service for Vocab entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo : VocabRepository = VocabRepository(db=self._uow.db)
        super().__init__(self._repo)

__all__ = ["VocabService"] 