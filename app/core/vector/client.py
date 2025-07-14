import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# 加载环境变量
# 从.env文件中读取配置信息，如API密钥等
# Load environment variables from .env file
load_dotenv()

# 从环境变量中获取Qdrant服务的URL
# 如果环境变量中没有设置，则使用默认值http://127.0.0.1:6333
# Get Qdrant service URL from environment variable
# If not set, use default value http://127.0.0.1:6333
qdrant_url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")

# 初始化Qdrant客户端
# 这个客户端将用于与Qdrant向量数据库进行交互
# Initialize Qdrant client for vector database operations
# この clientは Qdrant vector databaseと通信するために使用されます
client = QdrantClient(url=qdrant_url) 