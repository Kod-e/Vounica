import pytest
import pytest_asyncio
from httpx import AsyncClient
import logging, langchain
langchain.debug = True
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.order(21)
@pytest.mark.asyncio
async def test_start_learn(authenticated_async_client: AsyncClient):
    async with authenticated_async_client.stream(
        "POST",
        "/v1/question/agent/chat/stream",
        data={"user_input": "生成AI関連の英単語を学びたいので、それに合わせたレベルチェックをお願いします"},
        # data={"user_input": "i want learn some vocab for computer science"},
        # data={"user_input": "私は数学のちしきについてのえいごをまなびたいです"},
        # data={"user_input": "i want learn some vocab for computer science"},
        headers={
            "Accept-Language": "en",
            "Target-Language": "ja",
        },
        timeout=None,
    ) as response:
        async for chunk in response.aiter_lines():
            print(chunk)
    