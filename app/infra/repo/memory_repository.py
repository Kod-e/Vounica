from app.core.db.repository import Repository
from ..models import Memory
from typing import List, Protocol, Dict
from sqlalchemy import select, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

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
        
    
    # 根据重要性和时间排序, 获取用户最重要的几条记忆, 并且同时参考正在学习的语言匹配, 语言优先级更高
    async def get_user_memories(self, user_id: int, limit: int = 50, offset: int = 0, language: str = None) -> List[Memory]:
        """获取用户最重要的记忆，优先返回指定语言的记忆"""
        
        # 基础查询
        query = select(Memory).where(Memory.user_id == user_id)
        
        if language:
            # 创建动态排序权重：语言匹配的记录获得高优先级
            # 使用case语句创建一个虚拟列用于排序
            language_priority = case(
                (Memory.language == language, 1),  # 语言匹配时权重为1
                else_=0  # 语言不匹配时权重为0
            ).label("language_priority")
            
            # 首先按语言匹配排序，然后是常规的优先级和时间排序
            query = query.order_by(
                desc(language_priority),  # 语言匹配的排在前面
                desc(Memory.priority),    # 然后是优先级高的
                desc(Memory.created_at)   # 最后是时间新的
            )
        else:
            # 没有指定语言时使用原来的排序
            query = query.order_by(desc(Memory.priority), desc(Memory.created_at))
        
        # 添加分页
        query = query.offset(offset).limit(limit)
        
        # 执行查询
        result = await self.db.execute(query)
        return result.scalars().all()
        
    
    # 获取用户的所有记忆的category
    async def get_user_memory_categories(self, user_id: int) -> List[str]:
        """Get the user's all memory categories."""
        # 获取用户所有的记忆的category
        query = select(Memory.category).where(Memory.user_id == user_id).distinct()
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # 获取用户的所有记忆的category, 并且带上number, 方便AI理解,  返回结构是str:number
    async def get_category_counts(self, user_id: int) -> Dict[str, int]:
        """获取用户每个分类的记忆数量"""
        query = select(Memory.category, func.count(Memory.id).label('count')).where(
            Memory.user_id == user_id
        ).group_by(Memory.category)
        result = await self.db.execute(query)
        return {row.category: row.count for row in result}