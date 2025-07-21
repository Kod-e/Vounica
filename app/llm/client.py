from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI  # 最新 SDK

load_dotenv()


class OpenAIClient:

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str | None = None,
        default_embed_model: str = "text-embedding-3-small",
    ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self._client = OpenAI(api_key=api_key)
        self.default_model = default_model or os.getenv("OPENAI_MODEL", "gpt-4.1")
        self.default_embed_model = default_embed_model
    # 聊天接口
    def chat(self, *, messages: List[Dict[str, Any]], **kwargs):
        """Call chat completion and return raw response."""
        model = kwargs.pop("model", self.default_model)
        return self._client.chat.completions.create(model=model, messages=messages, **kwargs)

    # 向量化接口
    def embed(self, text: str, **kwargs) -> List[float]:
        """Return embedding vector for given text."""
        model = kwargs.pop("model", self.default_embed_model)
        resp = self._client.embeddings.create(model=model, input=text, **kwargs)
        return resp.data[0].embedding

_default_client = OpenAIClient()

chat_completion = _default_client.chat
embed = _default_client.embed