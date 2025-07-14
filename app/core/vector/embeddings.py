import os
from typing import List
from dotenv import load_dotenv
import openai


# 从.env文件中读取配置信息，特别是OpenAI API密钥
# Load environment variables from .env file, especially OpenAI API key
load_dotenv()

# 这个密钥用于访问OpenAI的API服务，包括文本嵌入模型
# Set OpenAI API key for accessing their services
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAI text-embedding-3-small 模型输出的向量维度为 1536
# 这个常量定义了嵌入向量的维度，用于创建向量集合时设置向量大小
# This constant defines the dimension of embedding vectors
EMBEDDING_DIMENSION = 1536


def get_embedding(text: str) -> List[float]:
    """
    使用 OpenAI 的 text-embedding-3-small 模型获取文本的嵌入向量
    
    Args:
        text: 需要嵌入的文本
        
    Returns:
        包含嵌入向量的浮点数列表
    """
    # 调用OpenAI的嵌入API，将文本转换为向量表示
    # 这个函数将文本发送到OpenAI的服务器，获取其向量表示
    # This function sends text to OpenAI's server and gets vector representation
    # textを vectorに変換するために OpenAIの APIを呼び出します
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding 