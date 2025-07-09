# 记录用户的故事
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.repositories.relational.base import BaseModel

