# 记录用户语法的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 语法习得状态表, 记录用户语法的习得状态
class Answer(BaseModel):
    """
    The Answer table by SQLAlchemy.
    これはAnswer Tableです。
    """
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # 答案的正文, 答案的正文需要可以被string化
    content = Column(Text)
    
    # 答案的类型, 答案的类型需要可以被string化
    type = Column(String(32))
    
    # 答案的习得状态, 这是在附近最近N次练习中, 答案被正确使用的概率, 从0-1
    status = Column(Float)