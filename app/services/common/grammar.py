# Grammar service wrapper
from app.services.common.common_base import BaseService
from app.infra.models.grammar import Grammar
from app.infra.repo.grammar_repository import GrammarRepository
from app.infra.context import uow_ctx


class GrammarService(BaseService[Grammar]):
    """Service for Grammar entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo: GrammarRepository = GrammarRepository(db=self._uow.db)
        super().__init__(self._repo)


__all__ = ["GrammarService"] 