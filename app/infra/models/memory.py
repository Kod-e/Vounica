# 记录用户语法的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 记忆表, 记录GPT对用户最近状态的描述
class Memory(BaseModel):
    """
    The Memory table by SQLAlchemy.
    これはMemory Tableです。
    """
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # This key is used to search the memory.
    # 记忆内容, 记忆内容需要可以被string化, 由LLM生成, 并且会vector化
    content = Column(Text)
    
    # This key is used to search the memory, and it is a tree structure.
    # 记忆的category, 最终这个category会作为一个Tree状目录
    category = Column(String(32))