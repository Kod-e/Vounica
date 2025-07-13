from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from sqlalchemy.sql import Select
from sqlalchemy.engine.result import ScalarResult

from app.repositories.relational.base import BaseModel

# 泛型类型变量，代表特定的模型类型
T = TypeVar('T', bound=BaseModel)

class Repository(Generic[T]):
    """
    The base repository class
    Provides generic CRUD operations that can be extended to implement specific business logic
    基本の repository class、　CRUD 操作を提供します。
    
    Uses asynchronous SQLAlchemy and yield-based session management
    Async SQLAlchemy と yield-based Session管理を使用します。
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize the repository
        
        Args:
            model: 
        """
        self.model = model
    
    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[T]:
        """
        根据 ID 获取实体
        
        Args:
            db: 数据库会话
            id: 实体 ID
            
        Returns:
            找到的实体，如果不存在则返回 None
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """
        获取实体列表
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            实体列表
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> T:
        """
        创建新实体
        
        Args:
            db: 数据库会话
            obj_in: 实体数据
            
        Returns:
            创建的实体
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, id: Any, obj_in: Dict[str, Any]) -> Optional[T]:
        """
        更新实体
        
        Args:
            db: 数据库会话
            id: 实体 ID
            obj_in: 更新的数据
            
        Returns:
            更新后的实体，如果不存在则返回 None
        """
        stmt = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def delete(self, db: AsyncSession, id: Any) -> Optional[T]:
        """
        删除实体
        
        Args:
            db: 数据库会话
            id: 实体 ID
            
        Returns:
            删除的实体，如果不存在则返回 None
        """
        # 先查询实体是否存在
        db_obj = await self.get_by_id(db, id)
        if db_obj:
            stmt = delete(self.model).where(self.model.id == id).returning(self.model)
            result = await db.execute(stmt)
            return result.scalars().first()
        return None
    
    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        检查实体是否存在
        
        Args:
            db: 数据库会话
            id: 实体 ID
            
        Returns:
            如果实体存在则返回 True，否则返回 False
        """
        query = select(self.model.id).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar() is not None
    
    async def count(self, db: AsyncSession) -> int:
        """
        获取实体总数
        
        Args:
            db: 数据库会话
            
        Returns:
            实体总数
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        result = await db.execute(query)
        return result.scalar() or 0
    
    # 可以根据需要添加更多通用方法
    # 如 get_by_field, find_with_filters 等 