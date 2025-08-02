import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.order(21)
@pytest.mark.asyncio
async def test_start_learn(authenticated_async_client: AsyncClient):
    async with authenticated_async_client.stream(
        "POST",
        "/v1/question/agent/chat/stream",
        data={"user_input": "生成AI関連の英単語を学びたいので、それに合わせたレベルチェックをお願いします"},
        headers={
            "Accept-Language": "ja",
            "Target-Language": "en",
        },
        timeout=None,
    ) as response:
        async for chunk in response.aiter_lines():
            print(chunk)
    