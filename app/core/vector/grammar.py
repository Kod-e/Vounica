import uuid
from typing import List

from qdrant_client import models
from qdrant_client.http.models import ScoredPoint

from app.core.vector.base import BaseVectorRepository
from app.core.vector.embeddings import get_embedding, EMBEDDING_DIMENSION


class GrammarVectorRepository(BaseVectorRepository):
    """
    Repository for grammar usages.
    This class handles vectorization and search for grammar usage examples.
    文法の使用例を vectorに変換して検索するための repositoryです。
    """
    
    def __init__(self):
        """
        Initialize the grammar vector repository.
        文法 vector repositoryを初期化します。
        """
        # 调用父类构造函数，设置集合名称和向量维度
        # 使用预定义的向量维度常量
        # Call parent constructor with collection name and vector dimension
        super().__init__(collection_name="grammars", vector_size=EMBEDDING_DIMENSION)

    def upsert_vector(self, relational_id: int, usage: str):
        """
        Upsert a vector for a grammar's usage.
        The vector ID will be a deterministic UUID based on the relational ID.
        
        Args:
            relational_id: ID of the grammar in the relational database
            usage: Grammar usage text to vectorize
        """
        # 基于关系ID生成确定性UUID
        # 这确保了同一个grammar_id总是对应相同的vector_id
        # Generate deterministic UUID based on relational ID
        # This ensures the same grammar_id always maps to the same vector_id
        vector_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"grammar-{relational_id}"))
        
        # 使用OpenAI的嵌入模型将语法用法文本转换为向量
        # Convert grammar usage text to vector using OpenAI's embedding model
        # 文法の使用例 textを vectorに変換します
        vector = get_embedding(usage)

        # 将向量和相关信息上传到Qdrant
        # 包括向量本身、ID和载荷（附加信息）
        # Upload vector and related information to Qdrant
        # Including the vector itself, ID and payload (additional information)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload={
                        "relational_id": relational_id,  # 关系数据库中的ID
                        "text": usage,  # 原始语法用法文本
                    },
                )
            ],
            wait=False,  # 异步上传，不等待操作完成
        )

    def search(self, text: str, limit: int = 5) -> List[ScoredPoint]:
        """
        Search for similar grammar usages.
        
        Args:
            text: Query text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of ScoredPoint objects containing similarity scores and payloads
        """
        # 将查询文本转换为向量
        # 使用与上传时相同的嵌入模型
        # Convert query text to vector using the same embedding model
        # query textを vectorに変換します
        vector = get_embedding(text)
        
        # 在Qdrant中搜索最相似的向量
        # 返回指定数量的最相似结果
        # Search for most similar vectors in Qdrant
        # Returns specified number of most similar results
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
        )