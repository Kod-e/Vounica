from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel

if TYPE_CHECKING:
    from app.infra.models.memory import Memory

# 从.env中获取默认token配额
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN_QUOTA = int(os.getenv("TOKEN_QUOTA", 1000))

# 用户表, 记录用户的基本信息
class User(BaseModel):
    """
    The User table by SQLAlchemy.
    これはUser Tableです。
    id: user's id
    name: user's name
    email: user's email
    password: user's password
    token_balance: user's token balance
    create_at and updated_at are defined in BaseModel.
    create_at と updated_at は BaseModel で定義されています。
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(254), unique=True, index=True)
    
    # 用户的token配额
    token_quota = Column(Integer, default=TOKEN_QUOTA)
    
    password = Column(String(256))
    
    # 用户的记忆列表
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.name}>"
    
    def __str__(self):
        return f"<User {self.name}>"