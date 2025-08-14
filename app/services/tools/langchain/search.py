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
从数据库检索用户在Vounica中记录的资源

你只能检索下方的这些支持的资源, 你可以视为数据库的表和字段
例如, 如果你需要检索vocab.name, 你应该使用resource=vocab, filed=name, 字段应该小写
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

如果你想进行语义查询(比如检索用户旅行相关的单词), 你应该用向量搜索
否则, 你应该输入一个合法的正则表达式
            """
        ),
        args_schema=SearchArgs,
    )