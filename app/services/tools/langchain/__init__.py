from .search import make_search_resource_tool
from app.infra.uow import UnitOfWork
from langchain_core.tools import StructuredTool
from typing import List



def make_tools() -> List[StructuredTool]:
    return [
        make_search_resource_tool()
    ]