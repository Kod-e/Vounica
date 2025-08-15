"""Vocab service wrapper."""

from typing import List
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

    # 获取list, 带分割
    async def get_user_vocabs(self, offset: int = 0, limit: int = 100) -> List[Vocab]:
        """Get the list of vocabs with split."""
        return await self._repo.get_user_vocabs(
            user_id=self._uow.current_user.id,
            offset=offset,
            limit=limit,
            language=self._uow.target_language
        )
    # 获取user有多少个记录的vocab, 返回Prompt
    async def get_user_vocab_count_prompt_for_agent(self) -> str:
        """Get the user's vocab count prompt for agent."""
        count = await self._repo.get_user_vocab_count(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language
        )
        result_str = f"##User has {count} vocabs\n"
        return result_str
__all__ = ["VocabService"] 