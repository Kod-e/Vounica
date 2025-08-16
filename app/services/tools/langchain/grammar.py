from ..function.grammar import add_grammar, record_grammar, add_and_record_grammar
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field

class GrammarAddArgs(BaseModel):
    name: str = Field(..., description="Grammar name")
    usage: str = Field(..., description="Grammar usage")

class GrammarRecordArgs(BaseModel):
    grammar_id: int = Field(..., description="Grammar ID")
    correct: bool = Field(..., description="Correct or incorrect")
    
class GrammarAddAndRecordArgs(BaseModel):
    name: str = Field(..., description="Grammar name")
    usage: str = Field(..., description="Grammar usage")
    correct: bool = Field(..., description="Correct or incorrect")
    
def make_grammar_add_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_grammar",
        coroutine=add_grammar,
        description="""
# 给用户添加一条语法习得记录
如果一个语法的name(在语言中实际的书写形式)和usage(在语言中的使用场景)相同或者非常相似, 那就视为一个语法
如果你通过数据库查询(通过正则匹配name), 并且发现有相同usage的语法, 那不应该调用这个函数导致重复添加
""",
        args_schema=GrammarAddArgs,
    )

def make_grammar_add_and_record_tool() -> StructuredTool:

    return StructuredTool.from_function(
        name="add_and_record_grammar",
        coroutine=add_and_record_grammar,
        description="""
# 给用户添加一条语法习得记录, 并且记录一次正确/错误
如果一个语法的name(在语言中实际的书写形式)和usage(在语言中的使用场景)相同或者非常相似, 那就视为一个语法
如果你通过数据库查询(通过正则匹配name), 并且发现有相同usage的语法, 那不应该调用这个函数导致重复添加
""",
        args_schema=GrammarAddAndRecordArgs,
    )

def make_grammar_record_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="record_grammar",
        coroutine=record_grammar,
        description="""
# 给用户记录一次语法习得记录
在你发现用户的回答中, 导致正确或者错误的关键部分和某个语法相关时, 如果用户正确或者错误的使用了这个语法, 那就调用这个函数
如果语法出现在题目无关的地方吗, 比如在题目中存在, 但是用户无论是否知道都不影响回答, 那就不应该调用这个函数
""",
        args_schema=GrammarRecordArgs,
    )
