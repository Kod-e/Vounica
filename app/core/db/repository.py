from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.sql import Select
from sqlalchemy.engine.result import ScalarResult

from app.core.db.base import BaseModel

# 泛型类型变量，代表特定的模型类型
T = TypeVar('T', bound=BaseModel)

class Repository(Generic[T]):
    """
    Generic asynchronous repository providing CRUD operations for SQLAlchemy models.

    汎用(はんよう)的(てき)な非同期(ひどうき)Repoです。CRUD 操作(そうさ)を提供(ていきょう)します。

    通用异步仓库，封装常见的 CRUD 操作。
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with the given model.

        指定(してい)された model ClassでRepoを初期化(しょきか)します。

        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        # 保存模型类供 CRUD 方法使用
    
    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[T]:
        """
        Retrieve a single record by primary key.

        主鍵(しゅけん)でrecordを取得(しゅとく)します。

        Args:
            db: Async database session
            id: Primary key value

        Returns:
            The found entity or ``None`` if not exists.
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve a list of records with optional pagination.

        record一覧(いちらん)を取得(しゅとく)します。pagination可能(かのう)。

        Args:
            db: Async database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            A list of entities
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> T:
        """
        Create a new record with the given data.

        渡(わた)されたdataでrecordを作成(さくせい)します。

        Args:
            db: Async database session
            obj_in: Data dict used to initialize the model

        Returns:
            The newly created entity
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, id: Any, obj_in: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing record by primary key.

        主鍵(しゅけん)で既存(きそん)recordを更新(こうしん)します。

        Args:
            db: Async database session
            id: Primary key value
            obj_in: Partial data dict with fields to update

        Returns:
            The updated entity or ``None`` when not found
        """
        stmt = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def delete(self, db: AsyncSession, id: Any) -> Optional[T]:
        """
        Delete a record by primary key.

        主鍵(しゅけん)でrecordを削除(さくじょ)します。

        Args:
            db: Async database session
            id: Primary key value

        Returns:
            The deleted entity or ``None`` when not found
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
        Check whether a record exists.

        recordの存在(そんざい)を確認(かくにん)します。

        Args:
            db: Async database session
            id: Primary key value

        Returns:
            ``True`` when exists, else ``False``
        """
        query = select(self.model.id).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar() is not None
    
    async def count(self, db: AsyncSession) -> int:
        """
        Count total number of records in the table.

        テーブル内(ない)のrecord総数(そうすう)を取得(しゅとく)します。

        Args:
            db: Async database session

        Returns:
            Total count of records
        """
        query = select(func.count()).select_from(self.model)
        result = await db.execute(query)
        return result.scalar() or 0
    
    # 可以根据需要添加更多通用方法
    # 如 get_by_field, find_with_filters 等 