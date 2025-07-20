
import os
import json
import pytest

# 默认模型，可通过环境变量 OPENAI_MODEL 替换。新版建议使用 "gpt-4.1"。
_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# Conditionally skip if no API key available
if not os.getenv("OPENAI_API_KEY"):
    pytest.skip("OPENAI_API_KEY not configured, skipping OpenAI test", allow_module_level=True)

# 兼容新版 / 旧版 openai SDK
try:
    # New style client (>= 1.0)
    from openai import OpenAI  # type: ignore

    _client = OpenAI()

    def _chat_completion(**kwargs):
        """Wrapper to create chat completion via new client."""
        return _client.chat.completions.create(**kwargs)

except ImportError:  # pragma: no cover
    import openai  # type: ignore

    openai.api_key = os.getenv("OPENAI_API_KEY")

    def _chat_completion(**kwargs):  # type: ignore
        """Wrapper to create chat completion via legacy API."""
        return openai.ChatCompletion.create(**kwargs)

# 本地 mock 函数
_fake_mistakes_db = {
    "user1": ["mistake1", "mistake2", "mistake3"],
    "user2": ["mistakeA"],
}

_fake_stories_db = {
    "zh": ["故事1", "故事2"],
    "en": ["story_en_1", "story_en_2"],
}

_fake_users = ["user1", "user2", "user3", "user4"]


def list_mistakes(user_id: str, limit: int = 5):
    """Return mistakes for a given user with optional limit."""
    return _fake_mistakes_db.get(user_id, [])[:limit]


def list_stories(language: str, limit: int = 1):
    """Return stories in specified language."""
    return _fake_stories_db.get(language, [])[:limit]


def list_users(limit: int = 50):
    """Return first *limit* users."""
    return _fake_users[:limit]


# 函数 schema 定义
_FUNCTION_SCHEMAS = [
    {
        "name": "list_mistakes",
        "description": "Return mistakes for a given user (optionally limited)",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Target user ID"},
                "limit": {
                    "type": "integer",
                    "description": "Max number of mistakes to return",
                    "default": 5,
                },
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "list_stories",
        "description": "Return stories in specified language (optionally limited)",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "Language code",
                    "enum": ["zh", "en", "ja"],
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of stories",
                    "default": 1,
                },
            },
            "required": ["language"],
        },
    },
    {
        "name": "list_users",
        "description": "Return users (optionally limited)",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Max number of users",
                    "default": 50,
                }
            },
            "required": [],
        },
    },
]


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI key and will incur API cost"
)
@pytest.mark.parametrize(
    "user_prompt,expected_fn_name,expected_args_keys",
    [
        ("请列出 3 个用户", "list_users", {"limit"}),
        ("帮我查看 user1 最近两道错题", "list_mistakes", {"user_id", "limit"}),
        ("给我展示一条中文故事", "list_stories", {"language", "limit"}),
    ],
)
def test_openai_dynamic_function_call(user_prompt, expected_fn_name, expected_args_keys):
    """Verify that the model selects the correct function and passes parameters."""

    # Build initial message
    messages = [{"role": "user", "content": user_prompt}]

    # Let model decide which function to invoke
    first_resp = _chat_completion(
        model=_DEFAULT_MODEL,
        messages=messages,
        functions=_FUNCTION_SCHEMAS,
        function_call="auto",
    )

    choice = first_resp.choices[0].message
    assert choice.function_call, (
        f"Model did not return function_call for prompt '{user_prompt}'"
    )

    called_fn = choice.function_call.name
    assert called_fn == expected_fn_name

    # Parse arguments JSON
    import json as _json
    args_dict = _json.loads(choice.function_call.arguments or "{}")
    # 验证包含必要参数
    assert expected_args_keys.issubset(args_dict.keys()), (
        f"Missing expected args {expected_args_keys} in {args_dict}"
    )

    # Map name -> func and invoke with parameters
    local_dispatch = {
        "list_users": list_users,
        "list_mistakes": list_mistakes,
        "list_stories": list_stories,
    }

    result_content = json.dumps(
        local_dispatch[called_fn](**args_dict), ensure_ascii=False
    )

    # 第二轮：将函数结果交给模型生成最终答复
    messages += [
        choice.to_dict(),
        {"role": "function", "name": called_fn, "content": result_content},
    ]

    second_resp = _chat_completion(
        model=_DEFAULT_MODEL,
        messages=messages,
    )

    final_msg = second_resp.choices[0].message
    assert final_msg.role == "assistant"
    # 简单断言：回复必须非空
    assert final_msg.content, "Assistant reply should not be empty"

    print("Prompt:", user_prompt)
    print("Model chose function:", called_fn, "with args", args_dict)
    print("Assistant reply:\n", final_msg.content) 