from ..function.vocab import add_vocab, record_vocab, add_and_record_vocab
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field

class VocabAddArgs(BaseModel):
    name: str = Field(..., description="Vocab name")
    usage: str = Field(..., description="Vocab usage")

class VocabRecordArgs(BaseModel):
    vocab_id: int = Field(..., description="Vocab's ID")
    correct: bool = Field(..., description="Correct or incorrect")
    
class VocabAddAndRecordArgs(BaseModel):
    name: str = Field(..., description="Vocab name")
    usage: str = Field(..., description="Vocab usage")
    correct: bool = Field(..., description="Correct or incorrect")
    
def make_vocab_add_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_vocab",
        coroutine=add_vocab,
        description="""
    # 给用户添加一条词汇习得记录
    如果一个词汇的name(在语言中实际的书写形式)和usage(在语言中的使用场景)相同或者非常相似, 那就视为一个词汇
    如果你通过数据库查询(通过正则匹配name), 并且发现有相同usage的词汇, 那不应该调用这个函数导致重复添加
""",
        args_schema=VocabAddArgs,
    )

def make_vocab_add_and_record_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_and_record_vocab",
        coroutine=add_and_record_vocab,
        description="""
# 给用户添加一条词汇习得记录, 并且记录一次正确/错误
如果一个词汇的name(在语言中实际的书写形式)和usage(在语言中的使用场景)相同或者非常相似, 那就视为一个词汇
如果你通过数据库查询(通过正则匹配name), 并且发现有相同usage的词汇, 那不应该调用这个函数导致重复添加
""",
        args_schema=VocabAddAndRecordArgs,
    )

def make_vocab_record_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="record_vocab",
        coroutine=record_vocab,
        description="""
# 给用户记录一次词汇习得记录
在你发现用户的回答中, 导致正确或者错误的关键部分和某个词汇相关时, 如果用户正确或者错误的使用了这个词汇, 那就调用这个函数
如果词汇出现在题目无关的地方吗, 比如在题目中存在, 但是用户无论是否知道都不影响回答, 那就不应该调用这个函数
""",
        args_schema=VocabRecordArgs,
    )
