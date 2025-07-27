from app.core.db.repository import Repository
from ..models import Memory
from typing import List, Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 增加一个Protocol, 用于定义MemoryRepository的接口
class MemoryRepositoryProtocol(Protocol):
    """Protocol for MemoryRepository."""
    
    # 定义函数, 全async
    async def get_user_memories(self, user_id: int, limit: int = 50) -> List[Memory]:
        """Get the user's most important memories."""

class MemoryRepository(Repository[Memory], MemoryRepositoryProtocol):
    """Repository class for Memory model.
    これは Memory model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Memory) 
        self.db = db
        
    
    # 根据重要性和时间排序, 获取用户最重要的几条记忆
    async def get_user_memories(self, user_id: int, limit: int = 50) -> List[Memory]:
        """Get the user's most important memories."""
        # 获取用户最重要的几条记忆, 按照重要性排序, 时间排序, 带limit
        query = select(Memory).where(Memory.user_id == user_id).order_by(Memory.priority.desc(), Memory.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()