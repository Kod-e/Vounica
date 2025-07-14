# 记录用户的故事
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db.base import BaseModel


# 故事表, 记录用户的故事
class Story(BaseModel):
    """
    The Story table by SQLAlchemy.
    これはStory Tableです。
    """
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # 故事的正文, 故事的正文需要可以被string化, 这个内容是GPT生成的, 并且会vector化
    content = Column(String)
    
    # 故事的摘要, 由LLM生成, 这会在LLM检索用户的喜好时被tree状的展现在llm的context中, 同时也会vector化
    summary = Column(String)
    
    # 故事的category, 最终这个category会作为一个Tree状目录, 这个category是用户自己定义的, 默认会进入"default"目录, GPT会给用户这个category的建议
    # 在命名建议前, GPT会知道用户有多少个Category建议, 并且会根据用户输入的story, 给出最合适的Category建议, 比如说用户已经有一个“最近的旅行‘ , 那这个category应该被归类进“最近的旅行”而不是新创建一个“最近去了哪里”
    category = Column(String)