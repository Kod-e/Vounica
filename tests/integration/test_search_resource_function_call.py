import os
import json
import pytest

from app.services.tools.search import ResourceLiteral

# 单一函数 schema
_SEARCH_SCHEMA = {
    "name": "search_resource",
    "description": "Unified regex / vector search on resources",
    "parameters": {
        "type": "object",
        "properties": {
            "resource": {
                "type": "string",
                "enum": ["vocab", "grammar", "mistake", "story", "memory"],
            },
            "field": {"type": "string"},
            "method": {"type": "string", "enum": ["regex", "vector"], "default": "regex"},
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 20},
        },
        "required": ["resource", "field", "query"],
    },
}

# 跳过测试条件：需要 OPENAI_API_KEY
if not os.getenv("OPENAI_API_KEY"):
    pytest.skip("OPENAI_API_KEY not configured, skip OpenAI function-call test", allow_module_level=True)

# 兼容新版 / 旧版 openai SDK
try:
    from openai import OpenAI  # type: ignore
    _client = OpenAI()

    def _chat_completion(**kw):
        return _client.chat.completions.create(**kw)
except ImportError:
    import openai  # type: ignore

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def _chat_completion(**kw):  # type: ignore
        return openai.ChatCompletion.create(**kw)

_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "o4-mini")


@pytest.mark.parametrize(
    "user_prompt,expected_resource,expected_field,expected_method",
    [
        ("请用向量搜索包含 bank 用法的词汇", "vocab", "usage", "vector"),
        ("搜一下故事概要里有 climate 的", "story", "summary", "regex"),
        ("帮我找 memory content vector 关于旅行 的记录", "memory", "content", "vector"),
    ],
)
@pytest.mark.asyncio
async def test_search_resource_function_call(
    user_prompt: str,
    expected_resource: ResourceLiteral,
    expected_field: str,
    expected_method: str,
):
    """Verify model selects correct search_resource parameters."""

    messages = [{"role": "user", "content": user_prompt}]

    first_resp = _chat_completion(
        model=_DEFAULT_MODEL,
        messages=messages,
        functions=[_SEARCH_SCHEMA],
        function_call="auto",
    )
# '{"resource":"story","field":"summary","method":"regex","query":"climate","limit":20}'
    choice = first_resp.choices[0].message
    assert choice.function_call, "Model did not choose function-call"
    assert choice.function_call.name == "search_resource"

    args = json.loads(choice.function_call.arguments or "{}")

    # 断言各参数
    assert args["resource"] == expected_resource
    assert args["field"] == expected_field
    assert args.get("method", "regex") == expected_method

    print("Prompt:", user_prompt)
    print("Model arguments:", args) 