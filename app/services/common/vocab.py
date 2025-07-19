"""Vocab service wrapper."""

from app.services.common.common_base import BaseService
from app.infra.models.vocab import Vocab
from app.infra.repo.vocab_repository import VocabRepository


class VocabService(BaseService[Vocab]):
    """Service for Vocab entity."""

    def __init__(self):
        super().__init__(VocabRepository())

__all__ = ["VocabService"] 