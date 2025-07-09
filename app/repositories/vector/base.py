from abc import ABC, abstractmethod
from qdrant_client import QdrantClient, models

from app.repositories.vector.client import client


class BaseVectorRepository(ABC):
    """
    Vector repository base class.
    This class provides common functionality for all vector repositories.
    Vector repositoryの基底classです。
    """
    
    def __init__(self, collection_name: str, vector_size: int):
        """
        Initialize the vector repository.
        
        Args:
            collection_name: Name of the vector collection
            vector_size: Dimension of vectors in the collection
        """
        # 初始化向量存储库的基本属性
        # 客户端用于与Qdrant数据库通信
        # Client is used to communicate with Qdrant database
        self.client: QdrantClient = client
        
        # 集合名称，用于在Qdrant中标识不同的向量集合
        # Collection name is used to identify different vector collections in Qdrant
        self.collection_name = collection_name
        
        # 向量维度，定义了存储在该集合中的向量的大小
        # Vector dimension defines the size of vectors stored in this collection
        # vectorの次元数を定義します
        self.vector_size = vector_size

    def create_collection(self):
        """
        Create a new collection if it does not exist.
        Collectionが存在しない場合、新しいcollectionを作成します。
        """
        # 检查集合是否已存在，如果不存在则创建
        # 这样可以避免重复创建集合导致的错误
        # Check if collection exists, create if not
        # This prevents errors from trying to create a collection that already exists
        if not self.client.collection_exists(self.collection_name):
            # 创建新的向量集合，设置向量大小和距离度量方式
            # Create a new vector collection with specified vector size and distance metric
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,  # 使用余弦相似度作为距离度量
                ),
            )

    @abstractmethod
    def upsert_vector(self, *args, **kwargs):
        """
        Abstract method for upserting vectors.
        This method must be implemented by subclasses.
        vectorを挿入または更新する抽象methodです。
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, *args, **kwargs):
        """
        Abstract method for searching vectors.
        This method must be implemented by subclasses.
        vectorを検索する抽象methodです。
        """
        raise NotImplementedError 