"""
OpenAI function call tools
"""

from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules
from typing import Any, Dict, List, Callable, Coroutine, Type

from app.core.uow import UnitOfWork


_FUNCTION_SCHEMAS: List[Dict[str, Any]] = []
_TOOL_MODULES: List[Any] = []
# 遍历所有子模块, 获得所有子模块
for _info in iter_modules(__path__):
    
    # 防止导入私有模块
    if _info.name.startswith("_"):
        continue

    # 遍历后, 等价于from app.services.tools.vocab import FUNCTION_SCHEMAS, make_dispatch
    _mod = import_module(f"{__name__}.{_info.name}")
    
    # 如果子模块符合了规则(有FUNCTION_SCHEMAS和make_dispatch)
    # 自动添加到_FUNCTION_SCHEMAS和_TOOL_MODULES列表中
    if hasattr(_mod, "FUNCTION_SCHEMAS") and hasattr(_mod, "make_dispatch"):
        #用extend函数添加到_FUNCTION_SCHEMAS列表中
        # 考虑到OpenAI到function call格式要求一个扁平的list dict
        # 如果用append会把一整个(比如2-3个dict)作为一个元素添加到列表中
        # 而extend会把每个dict平铺到列表中
        _FUNCTION_SCHEMAS.extend(getattr(_mod, "FUNCTION_SCHEMAS"))
        
        
        #用append函数添加到_TOOL_MODULES列表中
        _TOOL_MODULES.append(_mod)


FUNCTION_SCHEMAS: List[Dict[str, Any]] = _FUNCTION_SCHEMAS


def make_dispatch(uow: UnitOfWork) -> Dict:

    mapping: Dict = {}
    for mod in _TOOL_MODULES:
        mapping.update(mod.make_dispatch(uow))
    return mapping


__all__ = [
    "FUNCTION_SCHEMAS",
    "make_dispatch",
]
