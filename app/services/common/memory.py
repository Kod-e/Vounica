"""Memory service wrapper."""

import datetime
from typing import Any, List, Dict

from app.services.common.common_base import BaseService
from app.infra.models.memory import Memory
from app.infra.models.user import User
from app.infra.context import uow_ctx
from app.infra.repo.memory_repository import MemoryRepository 
from app.infra.schemas import MemoryCreateSchema, MemoryUpdateSchema

class MemoryService(BaseService[Memory]):
    """Service for Memory entity."""

    def __init__(self,):
        self._uow = uow_ctx.get()
        repo = MemoryRepository(db=self._uow.db)
        self._repo: MemoryRepository = repo
        super().__init__(repo)
    
    # 获取用户最重要的50条记忆, 不超过太多, 防止token消耗和focus丢失, 增加翻页功能
    async def get_user_memories(self, limit: int = 50,offset: int = 0) -> List[Memory]:
        """Get the user's most important memories."""
        # 利用MemoryRepository获取用户最重要的几条记忆
        return await self._repo.get_user_memories(
            user_id=self._uow.current_user.id, 
            limit=limit,
            offset=offset,
            language=self._uow.target_language
        )
    # 获取用户最重要的50条记忆, 并且返回一个list dict, 用于给AI看
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
            user_id=self._uow.current_user.id
        )
        
    # 获取用户的所有记忆的category, 并且带上number, 方便AI理解,  返回结构是str:number
    async def get_user_memory_categories_with_number(self) -> Dict[str, int]:
        """Get the user's all memory categories with number."""
        # 利用MemoryRepository获取用户所有的记忆的category
        categories = await self._repo.get_category_counts(
            user_id=self._uow.current_user.id
        )
        return categories
    
    # 从Category中获取记忆list
    async def get_memory_by_category(self, category: str, limit: int = 50, offset: int = 0) -> List[Memory]:
        """Get the user's memories by category."""
        return await self._repo.get_memory_by_category(
            user_id=self._uow.current_user.id,
            category=category,
            limit=limit,
            offset=offset
        )


__all__ = ["MemoryService"] 