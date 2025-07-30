"""
开发时用于让LLM把一段内容发送到控制台, 用于调试
"""

from __future__ import annotations


SEND_CONSOLE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "send_console",
        "description": "Send a message to the console",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "The message to send to the console"},
            },
            "required": ["message"],
        },
    },
}

async def send_console(message: str) -> None:
    """Send a message to the console"""
    print(message)