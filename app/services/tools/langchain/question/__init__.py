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
        built = build(stack)
        if isinstance(built, list):
            tools.extend(built)
        elif built is not None:
            tools.append(built)
    return tools 