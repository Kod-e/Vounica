from dotenv import load_dotenv
from langchain_core.tools import Tool,ArgsSchema,StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
import datetime
import logging, langchain
langchain.debug = True
logging.basicConfig(level=logging.INFO)
from app.services.tools.langchain.search import make_search_resource_tool
from app.infra.uow import UnitOfWork
import pytz
from pydantic import BaseModel
import asyncio
# 1. 加载环境变量（比如 OpenAI API Key）


from pydantic import BaseModel, Field


async def main():
    load_dotenv()
    tools = [
        make_search_resource_tool(uow=UnitOfWork())
        # make_a_fake_tool()
    ]

    # 3. 实例化 LLM
    model = ChatOpenAI(model="gpt-4.1")

    # 4. 创建内存存储器
    checkpointer = InMemorySaver()

    # 5. 创建 ReAct Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer
    )

    # 6. 运行 Agent - 第一个问题
    config = {"configurable": {"thread_id": "1"}}
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "关于我在麦当劳点餐时的用语, 有什么修改的建议吗, 去数据库检索一下之前的使用例子"}]},
        config
    )
    last_message = response["messages"][-1]
    print("问题1回答:", last_message.content)
    
if __name__ == "__main__":
    asyncio.run(main())