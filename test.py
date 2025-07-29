from dotenv import load_dotenv
from langchain_core.tools import Tool,ArgsSchema,StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.language_models import LanguageModelInput
from app.infra import quota
from app.services.question.types.choice import ChoiceQuestion
from app.services.tools.langchain.search import make_search_resource_tool
from app.infra.uow import UnitOfWork
import pytz
from pydantic import BaseModel
import asyncio
# 1. 加载环境变量（比如 OpenAI API Key）


from pydantic import BaseModel, Field
