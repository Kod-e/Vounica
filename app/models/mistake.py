# 错题集记录时, 记录整个题目的string内容, 并且让GPT生成错在哪里的评价
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.repositories.relational.base import BaseModel


# 错题集表, 记录用户的基本信息
class Mistake(BaseModel):
    """
    The Mistake table by SQLAlchemy.
    これはMistake Tableです。
    """
    __tablename__ = "mistakes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # 题目内容, 每个题目都应该可以被string化, 并且可以被LLM生成评价
    question = Column(String)
    
    # 题目类型, 题目的类型可以使用string来表示
    question_type = Column(String)
    
    # 题目的需要练习的语言类型, 可以使用string来表示
    language_type = Column(String)

    #回答内容, 每个题目的回答都应该可以被string化, 并且可以被LLM生成评价
    answer = Column(String)
    
    # 正确答案, 每个题目的正确答案都应该可以被string化, 并且可以被LLM生成评价
    correct_answer = Column(String)
    
    # 错误原因, 错误原因应该由LLM根据Prompt生成
    error_reason = Column(String)
    
    def __repr__(self):
        return f"<Mistake {self.id}>"
    
    def __str__(self):
        return f"<Mistake {self.id}>"