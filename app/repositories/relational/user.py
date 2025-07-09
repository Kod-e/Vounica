from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.repositories.relational.base import BaseModel


# 用户表, 记录用户的基本信息
class User(BaseModel):
    """
    The User table by SQLAlchemy.
    これはUser Tableです。
    id: ユーザーID
    name: ユーザー名
    email: ユーザーのメールアドレス
    password: ユーザーのパスワード
    
    create_at and updated_at are defined in BaseModel.
    create_at と updated_at は BaseModel で定義されています。
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    def __repr__(self):
        return f"<User {self.name}>"
    
    def __str__(self):
        return f"<User {self.name}>"