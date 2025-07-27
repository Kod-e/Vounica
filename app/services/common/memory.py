"""Memory service wrapper."""

import datetime
from typing import Any, List, Dict

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
        
    # 获取用户最重要的50条记忆, 不超过太多, 防止token消耗和focus丢失, 增加翻页功能
    async def get_user_memories(self, limit: int = 50,offset: int = 0) -> List[Memory]:
        """Get the user's most important memories."""
        # 利用MemoryRepository获取用户最重要的几条记忆
        return await self._repo.get_user_memories(
            user_id=self._uow.current_user_id, 
            limit=limit,
            offset=offset,
            language=self._uow.target_language
        )
    # 获取用户最重要的50条记忆, 并且返回一个list string, 用于给AI看
    async def get_user_memories_list(self, limit: int = 50,offset: int = 0) -> List[Dict[str, Any]]:
        """Get the user's most important memories."""
        # 利用MemoryRepository获取用户最重要的几条记忆
        memories = await self.get_user_memories(limit=limit,offset=offset)
        return [{
            "content": memory.content,
            "category": memory.category,
            "priority": memory.priority,
            "created_at": memory.updated_at.isoformat()
        } for memory in memories]
    # 获取用户的所有记忆的category
    async def get_user_memory_categories(self) -> List[str]:
        """Get the user's all memory categories."""
        # 利用MemoryRepository获取用户所有的记忆的category
        return await self._repo.get_user_memory_categories(
            user_id=self._uow.current_user_id,
            language=self._uow.target_language
        )
    # 获取用户的所有记忆的category, 并且带上number, 方便AI理解,  返回结构是str:number
    async def get_user_memory_categories_with_number(self) -> Dict[str, int]:
        """Get the user's all memory categories with number."""
        # 利用MemoryRepository获取用户所有的记忆的category
        categories = await self._repo.get_category_counts(
            user_id=self._uow.current_user_id,
            language=self._uow.target_language
        )
        return categories

__all__ = ["MemoryService"] 