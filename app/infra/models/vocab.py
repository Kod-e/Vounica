# 记录用户单词的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 单词习得状态表, 记录用户单词的习得状态
class Vocab(BaseModel):
    """
    The Vocab table by SQLAlchemy.
    """
    __tablename__ = "vocabs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # 单词的名称, 单词的名称需要可以被string化
    name = Column(String(32))
    
    # 单词的使用场景, 单词的使用场景需要可以被string化, 并且应该由LLM生成
    usage = Column(Text)
    
    # 单词的习得状态, 这是在附近最近N次练习中, 单词被正确使用的概率, 从0-1
    status = Column(Float)

    # SRS 相关字段
    correct_rate = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    last_review_at = Column(DateTime)
    next_review_at = Column(DateTime)
    easiness_factor = Column(Float, default=2.5)
    
    
    # 语言, ISO 639-1 code，例如 "en", "ja", "zh"
    language = Column(String(8))