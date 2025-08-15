# 记录用户语法的习得状态
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel
if TYPE_CHECKING:
    from app.infra.models.user import User

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
    
    # 记忆的摘要
    summary = Column(String(64))
    # This key is used to search the memory, and it is a tree structure.
    # 记忆的category, 最终这个category会作为一个Tree状目录
    category = Column(String(32))

    # 记忆的语言, ISO 639-1 code，例如 "en", "ja", "zh"
    language = Column(String(8))

    # 优先级, 数值越高越先被注入 GPT 上下文
    priority = Column(Integer, default=0)
    
    # 用户
    user = relationship("User", back_populates="memories")