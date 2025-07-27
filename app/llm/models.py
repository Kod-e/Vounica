from __future__ import annotations

import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# 模型ID配置
OPENAI_MODEL_LOW = os.getenv("OPENAI_MODEL_LOW", "gpt-4o-mini")
OPENAI_MODEL_STADARD = os.getenv("OPENAI_MODEL_STADARD", "o4-mini")
OPENAI_MODEL_HIGH = os.getenv("OPENAI_MODEL_HIGH", "o3")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# 模型价格配置 (1M tokens/USD)
OPENAI_MODEL_LOW_PRICE = int(os.getenv("OPENAI_MODEL_LOW_PRICE", "15"))
OPENAI_MODEL_STADARD_PRICE = int(os.getenv("OPENAI_MODEL_STADARD_PRICE", "110"))
OPENAI_MODEL_HIGH_PRICE = int(os.getenv("OPENAI_MODEL_HIGH_PRICE", "200"))
OPENAI_EMBED_MODEL_PRICE = int(os.getenv("OPENAI_EMBED_MODEL_PRICE", "2"))


class LLMModel(Enum):
    """
    语言模型枚举类
    
    为不同的模型定义名称、价格和其他属性，方便统一管理和使用
    """
    # 低成本模型，适合简单任务
    LOW = {
        "name": OPENAI_MODEL_LOW,
        "price": OPENAI_MODEL_LOW_PRICE,
        "description": "低成本模型，适合简单任务"
    }
    
    # 标准模型，成本和性能平衡
    STANDARD = {
        "name": OPENAI_MODEL_STADARD,
        "price": OPENAI_MODEL_STADARD_PRICE,
        "description": "标准模型，平衡成本和性能"
    }
    
    # 高质量模型，适合复杂推理
    HIGH = {
        "name": OPENAI_MODEL_HIGH,
        "price": OPENAI_MODEL_HIGH_PRICE,
        "description": "高质量模型，适合复杂推理任务"
    }
    
    # 嵌入模型，用于文本向量化
    EMBED = {
        "name": OPENAI_EMBED_MODEL,
        "price": OPENAI_EMBED_MODEL_PRICE,
        "description": "文本嵌入模型"
    }
    
    @property
    def model_name(self) -> str:
        """获取用于API调用的实际模型名称"""
        return self.value["name"]
    
    @property
    def price(self) -> int:
        """获取每百万tokens的价格（0.01USD）"""
        return self.value["price"]
    
    @property
    def description(self) -> str:
        """获取模型描述"""
        return self.value["description"] 