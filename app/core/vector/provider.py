"""
Store a singleton QdrantClient that will be injected once at application startup.

QdrantClient を保持(ほじ)し、`set_qdrant_client()` で注入(ちゅうにゅう)してから
`get_qdrant_client()` で取得(しゅとく)します。
"""

from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

_client: QdrantClient | None = None


def set_qdrant_client(client: QdrantClient) -> None:
    """Inject a ready-to-use QdrantClient from outer layer."""
    global _client
    _client = client


def get_qdrant_client() -> QdrantClient:
    """Retrieve the globally stored QdrantClient, or raise if not yet set."""
    if _client is None:
        raise RuntimeError(
            "Qdrant client not set. Call set_qdrant_client() during application startup."
        )
    return _client


# ------------------------------------------------------------------
# Factory helper
# ------------------------------------------------------------------


def make_qdrant_client() -> QdrantClient:
    """
    Create a QdrantClient from environment variables and inject it into the core provider.

    環境(かんきょう)変数(へんすう)から QdrantClient を作成(さくせい)し、provider へ注入(ちゅうにゅう)します。
    """
    # 加载环境变量
    load_dotenv()
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    client = QdrantClient(url=qdrant_url)

    # 设置qdrant client
    set_qdrant_client(client)
    return client 