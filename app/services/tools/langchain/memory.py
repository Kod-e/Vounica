from ..function.memory import add_memory, update_memory, delete_memory
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field

class MemoryAddArgs(BaseModel):
    category: str = Field(..., 
        description="记忆的分类, 用于在把记忆传递给你的时候, 能够格式化")
    summary: str = Field(..., 
        description="记忆的摘要, 用于简述这个记忆的内容, 需要严格限定在String(64)以内")
    content: str = Field(..., 
        description="完整的内容, 需要在这里完整的描述在这个记忆中关于用户的行为")
    priority: int = Field(0, description="记忆的优先级, 数字越高, 优先级越高, 默认为0")

class MemoryUpdateArgs(BaseModel):
    memory_id: int = Field(..., description="Memory ID")
    category: str = Field(..., description="记忆的分类, 用于在把记忆传递给你的时候, 能够格式化")
    summary: str = Field(..., description="记忆的摘要, 用于简述这个记忆的内容, 需要严格限定在String(64)以内")
    content: str = Field(..., description="完整的内容, 需要在这里完整的描述在这个记忆中关于用户的行为")
    priority: int = Field(0, description="记忆的优先级, 数字越高, 优先级越高, 默认为0")

class MemoryDeleteArgs(BaseModel):
    memory_id: int = Field(..., description="Memory ID")

def make_memory_add_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_memory",
        coroutine=add_memory,
        description="""
添加一条记忆到数据库中, 当你添加之后, 就会按照category制作一个tree状列表, 并且每次调用时都会把summary回传给你
你需要记住一些对于用户比较重要的信息, 但是不要存储过于短期的信息, 比如用户今天下午的行程
如果用户的某条记忆过时了, 请使用update_memory来更新, 或者使用delete_memory来删除, 而不是重新添加一条
""",
        args_schema=MemoryAddArgs,
    )
    
def make_memory_update_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="update_memory",
        coroutine=update_memory,
        description="""
更新一条记忆, 用于改变某些过时的记忆或者错误的记忆
一般建议更新时, 留半句话描述之前的状态, 之后重新描述在某一点上改变了什么, 但是请只留在content中, 在summary中只简短的描述当下的内容
如果之前的状态对于当下或者以后已经无关紧要而且不会被重新提起的话, 那可以完全覆盖现有的内容
""",
        args_schema=MemoryUpdateArgs,
    )
    
def make_memory_delete_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="delete_memory",
        coroutine=delete_memory,
        description="""
删除一条记忆, 用于删除某些过时的记忆或者错误的记忆, 或者用户不喜欢这个记忆, 或者用户已经不需要这个记忆了
""",
        args_schema=MemoryDeleteArgs,
    )
    
def make_memory_tool() -> StructuredTool:
    return [
        make_memory_add_tool(),
        make_memory_update_tool(),
        make_memory_delete_tool(),
    ]