from ..function import search_resource
from langchain_core.tools import StructuredTool
from functools import partial
from pydantic import BaseModel, Field


# 搜索参数
class SearchArgs(BaseModel):
    resource: str = Field(..., description="资源类型")
    field:    str = Field(..., description="资源字段")
    query:    str = Field(..., description="向量搜索传递语意匹配的内容|否则是一个合法的正则表达式")
    is_vector:   bool = Field(False, description="如果为True, 则使用向量搜索, 否则使用正则表达式搜索")
    limit:    int = Field(20, description="查询数量")

# 制作函数, 注入应该注入的内容
def make_search_resource_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="search_resource",
        coroutine=search_resource,
        description=(
            """
检索用户在Vounica中记录的资源
Vocab: 用户单词的习得状态
Grammar 用户语法的习得状态
Memory 你对用户的记忆, 这个Memory只能通过LLM填写
Story 用户自己记录的关于自己的故事和笔记
Mistake 用户的错题本
支持的资源
vocab.name 单词名称
vocab.usage 单词使用场景, 由LLM生成
grammar.name 语法名称
grammar.usage 语法使用场景, 由LLM生成
memory.content 记忆的内容
story.category 故事的分类
mistake.question 问题内容
mistake.answer 用户的回答
mistake.correct_answer 正确回答
mistake.error_reason 错误原因, 由LLM生成
            """
        ),
        args_schema=SearchArgs,
    )