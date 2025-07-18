# 记录用户语法的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 语法习得状态表, 记录用户语法的习得状态
class Grammer(BaseModel):
    """
    The Grammer table by SQLAlchemy.
    これはMistake Tableです。
    """
    __tablename__ = "grammers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # 语法的名称, 语法的名称需要可以被string化
    name = Column(String(32))
    
    # 语法的使用场景, 语法的使用场景需要可以被string化
    usage = Column(Text)
    
    # 语法的习得状态, 这是在附近最近N次练习中, 语法被正确使用的概率, 从0-1
    status = Column(Float)