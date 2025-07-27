"""Memory service wrapper."""

from typing import List

from app.services.common.common_base import BaseService
from app.infra.models.memory import Memory
from app.infra.models.user import User
from app.infra.uow import UnitOfWork
from app.infra.repo.memory_repository import MemoryRepository 


class MemoryService(BaseService[Memory]):
    """Service for Memory entity."""

    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        repo = MemoryRepository(db=uow.db)
        self._repo: MemoryRepository = repo
        super().__init__(repo)
        
    # 获取用户最重要的50条记忆, 不超过太多, 防止token消耗和focus丢失
    async def get_user_memories(self, limit: int = 50) -> List[Memory]:
        """Get the user's most important memories."""
        # 利用MemoryRepository获取用户最重要的几条记忆
        return await self._repo.get_user_memories(
            user_id=self._uow.current_user_id, 
            limit=limit
        )


__all__ = ["MemoryService"] 