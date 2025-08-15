from app.services.agent.core.core import CoreAgent
from app.services.question.types import QuestionUnion
from app.services.logic.question import QuestionHandler
from typing import List
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.services.tools.langchain import make_search_resource_tool

class RecordAgent(CoreAgent):
    def __init__(self):
        super().__init__()
        # 题目
        self.questions = []
        self.judge_results = []
                        
    async def run(self, questions: List[QuestionUnion]):
        # 判断所有的题目
        question_handler = QuestionHandler()
        self.judge_results = await question_handler.record(questions)
        
        # 创建Agent
        record_agent = create_react_agent(
            model=self.high_model,
            tools=[
                make_search_resource_tool()
            ],
            checkpointer=self.checkpointer
        )
        