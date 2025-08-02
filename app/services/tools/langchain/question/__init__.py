# 新建
"""Question tool package.

遍历当前子包下的模块，收集 `build_tools(stack)` 返回的 StructuredTool 列表，
供 `QuestionStack` 使用。"""

from __future__ import annotations

import importlib
import pkgutil
from typing import List

from langchain_core.tools import StructuredTool


def gather_tools(stack) -> List[StructuredTool]:
    """遍历子模块，收集工具。"""
    tools: List[StructuredTool] = []
    pkg = __name__  # e.g. app.services.tools.langchain.question
    for info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{pkg}.{info.name}")
        build = getattr(module, "build_tools", None)
        if build is None:
            continue
        # 对每个子模块注入 QuestionStack 的内部列表 `questions`，
        # 避免在 add_*_question 中直接调用 `append` 时出现属性缺失错误。
        built = build(stack.questions)
        if isinstance(built, list):
            tools.extend(built)
        elif built is not None:
            tools.append(built)
    return tools 