from dotenv import load_dotenv
from langchain_core.tools import Tool,ArgsSchema,StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.language_models import LanguageModelInput
from app.infra.context import uow_ctx
from app.infra.uow import UnitOfWork
import asyncio
import logging
# 1. 加载环境变量（比如 OpenAI API Key）
from app.services.tools.langchain.question_stack import QuestionStack
from app.services.tools.langchain.question.choice import build_tools
logging.basicConfig(level=logging.DEBUG)



async def main():
    uow = UnitOfWork()
    uow_ctx.set(uow)
    qustion_stack = QuestionStack()

    qustion_tools = qustion_stack.get_tools()


    agent = create_react_agent(
        model=ChatOpenAI(model="gpt-4.1"),
        tools=[
            *qustion_tools
        ],
        checkpointer=InMemorySaver()
    )
    config = {"configurable": {"thread_id": "1"}}
    response = await agent.ainvoke(
        {"messages": [
            {"role": "system", "content": "你是一个语言学习平台的题目生成代理, 用户正在学习en语言(ISO 639-1 标准), 题目一定需要满足练习这件事情的要求 ,有指向性, 答案唯一, 并且你应该保证题型的多元化,不能只有一种题目,你的题目应该仅仅包含语言学习, 不应该包含一些其他的内容(比如部分专业知识)你需要按照要求调用function生成后, 告诉用户你做了什么"},
            {"role": "user", "content": "生成5个可能会用旅行相关的题目"},
        ]},
        config
    )
    print(response['messages'][-1].content)
    for question in qustion_stack.questions:
        print(question.prompt())

if __name__ == "__main__":
    asyncio.run(main())


