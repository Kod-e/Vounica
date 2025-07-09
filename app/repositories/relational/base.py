from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

Base = declarative_base()

# 增加基础的表, 定义created_at和updated_at
class BaseModel(Base):
    """
    The base model for all tables.
    これはすべてのTableのBaseModelです。
    created_at: 作成日時
    updated_at: 更新日時
    """
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)