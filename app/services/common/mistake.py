"""Mistake service wrapper.

Mistakeモデル用 CRUD + ベクター同期 Service
"""

from app.services.common.common_base import BaseService
from app.infra.models.mistake import Mistake
from app.infra.repo.mistake_repository import MistakeRepository
from app.infra.uow import UnitOfWork
from typing import List

class MistakeService(BaseService[Mistake]):
    """Service for Mistake entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        self._repo : MistakeRepository = MistakeRepository(db=uow.db)
        super().__init__(self._repo)

    # 获取用户最近的5道错题, 用于让LLM知道用户之前犯了什么错
    async def get_user_mistakes(self, limit: int = 5,offset: int = 0) -> List[Mistake]:
        """Get the user's recent mistakes."""
        return await self._repo.get_user_mistakes(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language,
            limit=limit,
            offset=offset
        )

__all__ = ["MistakeService"] 