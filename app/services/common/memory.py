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
        
    # 获取数据库里关于User Memory数量的统计
    async def get_user_memory_count_prompt_for_agent(self) -> str:
        """Get the user's memory count."""
        result_str = "#User's Memory Count\n"
        count_dict = await self._repo.get_category_counts(
            user_id=self._uow.current_user.id
        )
        if len(count_dict) == 0:
            result_str += "No Any memory\n"
        else:
            for category, count in count_dict.items():
                result_str += f"{category}: {count}\n"
        return result_str
        
    # 获取用户最重要的N条记忆的summar, 并且分类
    async def get_user_memory_summary_prompt_for_agent(self, limit: int = 150) -> str:
        """Get the user's most important memories summary."""
        result_dict = {}
        # 利用MemoryRepository获取用户最重要的几条记忆
        memories = await self._repo.get_memory_by_language(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language,
            limit=limit
        )
        result_str = "#User's Memory Summary\n"
        result_str += f"ID|Time|Summary|Priority|Language ISO 639-1(if is not from target language, it will be show, if is from target language, it will be hidden)\n"
        if len(memories) == 0:
            result_str += "No Any memory\n"
            return result_str
        for memory in memories:
            # 检测result_dict里是否存在memory.category, 如果不存在, 则添加
            if memory.category not in result_dict:
                result_dict[memory.category] = []
            # 添加memory.summary到result_dict[memory.category]
            # 如果不是当前语言, 后方添加来自其他语言
            if memory.language != self._uow.target_language:
                result_dict[memory.category].append(
                    f"{memory.id}|{memory.updated_at.strftime('%Y-%m-%d')}|{memory.summary}|{memory.priority}|THIS MEMORY IS FROM {memory.language}"
                )
            else:
                result_dict[memory.category].append(
                    f"{memory.id}|{memory.updated_at.strftime('%Y-%m-%d')}|{memory.summary}|{memory.priority}"
            )
        # 遍历result_dict的key
        for category, memories in result_dict.items():
            result_str += f"##{category}\n"
            for memory in memories:
                result_str += f"{memory}\n"
        return result_str

__all__ = ["MemoryService"] 