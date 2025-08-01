from ..function.memory import add_memory, update_memory, delete_memory
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field

class MemoryAddArgs(BaseModel):
    category: str = Field(..., description="Memory category")
    content: str = Field(..., description="Memory content")
    priority: int = Field(0, description="Memory priority")

class MemoryUpdateArgs(BaseModel):
    memory_id: int = Field(..., description="Memory ID")
    category: str = Field(..., description="Memory category")
    content: str = Field(..., description="Memory content")
    priority: int = Field(0, description="Memory priority")

class MemoryDeleteArgs(BaseModel):
    memory_id: int = Field(..., description="Memory ID")

def make_memory_add_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_memory",
        coroutine=add_memory,
        description="Add a memory",
        args_schema=MemoryAddArgs,
    )
    
def make_memory_update_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="update_memory",
        coroutine=update_memory,
        description="Update a memory",
        args_schema=MemoryUpdateArgs,
    )
    
def make_memory_delete_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="delete_memory",
        coroutine=delete_memory,
        description="Delete a memory",
        args_schema=MemoryDeleteArgs,
    )
    
def make_memory_tool() -> StructuredTool:
    return [
        make_memory_add_tool(),
        make_memory_update_tool(),
        make_memory_delete_tool(),
    ]