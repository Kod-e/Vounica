# 记录用户语法的习得状态
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 语法习得状态表, 记录用户语法的习得状态
class Grammar(BaseModel):
    """
    The Grammar table by SQLAlchemy.
    これはMistake Tableです。
    """
    __tablename__ = "grammars"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # 语法的名称, 语法的名称需要可以被string化
    name = Column(String(32))
    
    # 语法的使用场景, 语法的使用场景需要可以被string化
    usage = Column(Text)
    
    # 语法的习得状态, 这是在附近最近N次练习中, 语法被正确使用的概率, 从0-1
    status = Column(Float)

    # SRS 相关字段

    # 近期正确率 (0~1)
    correct_rate = Column(Float, default=0.0)

    # 累计复习次数
    review_count = Column(Integer, default=0)

    # 上次复习时间(一开始准备使用的, 不过看起来项目中没用到)
    last_review_at = Column(DateTime)

    # 下一次复习时间（SRS 算法计算）(一开始准备使用的, 不过看起来项目中没用到)
    next_review_at = Column(DateTime)

    # SM-2 easiness factor，默认 2.5(一开始准备使用的, 不过看起来项目中没用到)
    easiness_factor = Column(Float, default=2.5)
    
    # 语言, ISO 639-1 code，例如 "en", "ja", "zh"
    language = Column(String(8))