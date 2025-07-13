# 记录用户单词的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.repositories.relational.base import BaseModel


# 单词习得状态表, 记录用户单词的习得状态
class Vocab(BaseModel):
    """
    The Vocab table by SQLAlchemy.
    """
    __tablename__ = "vocabs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 单词的名称, 单词的名称需要可以被string化
    name = Column(String)
    
    # 单词的使用场景, 单词的使用场景需要可以被string化, 并且应该由LLM生成
    usage = Column(String)
    
    # 单词的习得状态, 这是在附近最近N次练习中, 单词被正确使用的概率, 从0-1
    status = Column(Float)