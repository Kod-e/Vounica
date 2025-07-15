# 仓库层(base_repository) 定义

from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db.base import BaseModel  # 假设你有个所有模型继承的 Base

# 定义一个泛型, 这个泛型是BaseModel的子类
ModelType = TypeVar("ModelType", bound=BaseModel)

# 定义一些基础的CRUD操作
class BaseRepository(Generic[ModelType]):
    """
    The BaseRepository class for all repositories.
    これはすべてのRepositoryの基本(きほん)クラスです。
    """
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).get(id)

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        obj = self.get_by_id(obj_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False