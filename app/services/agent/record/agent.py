from app.services.agent.core.core import CoreAgent
from app.services.question.types import QuestionUnion
from app.services.logic.question import QuestionHandler
from pydantic import BaseModel
from typing import List
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from app.services.tools.langchain import make_search_resource_tool, make_memory_add_tool, make_memory_update_tool, make_memory_delete_tool, make_vocab_add_and_record_tool, make_vocab_record_tool, make_grammar_add_and_record_tool, make_grammar_record_tool
from app.services.common.memory import MemoryService
from app.services.common.grammar import GrammarService
from app.services.common.story import StoryService
from app.services.common.mistake import MistakeService
from app.services.common.vocab import VocabService
from app.services.agent.record.schema import RecordAgentEvent, RecordAgentResultData, RecordAgentResultEvent

class SetSuggestionArgs(BaseModel):
    suggestion: str

class RecordAgent(CoreAgent):
    def __init__(self):
        super().__init__()
        # 题目
        self.questions = []
        self.memory_service = MemoryService()
        self.grammar_service = GrammarService()
        self.story_service = StoryService()
        self.mistake_service = MistakeService()
        self.vocab_service = VocabService()
        self.question_handler = QuestionHandler()
        self.judge_results = []
        # 建议(一段string, 用于描述用户应该如何改进)
        self.suggestion = ""
        
    def edit_suggestion(self, suggestion: str):
        self.suggestion = suggestion
        return "##suggestion\n" + self.suggestion
    
    async def run(self, questions: List[QuestionUnion]):
        await self.record_questions(questions)
        await self.make_suggestion()
        self.event(RecordAgentResultEvent(
            data=RecordAgentResultData(
                suggestion=self.suggestion,
                judge_results=self.judge_results
            )
        ))
    async def make_suggestion(self):
        tool = StructuredTool.from_function(
            name="set_suggestion",
            coroutine=self.set_suggestion,
            description="给用户生成一个文字建议",
            args_schema=SetSuggestionArgs
        )
        suggestion_agent = create_react_agent(
            model=self.model,
            tools=[tool],
            checkpointer=self.checkpointer
        )
        config = {"configurable": {"thread_id": "1"}}
        payload = {"messages": [{"role": "system", "content": "根据之前用户的回答, 给用户生成建议"}]}
        await self.run_stream_events(
            agent=suggestion_agent,
            payload=payload,
            config=config,
        )
        
    async def set_suggestion(self, suggestion: str):
        self.suggestion = suggestion
        return "##suggestion\n" + self.suggestion
    
    async def record_questions(self, questions: List[QuestionUnion]):
        # 判断所有的题目
        self.questions = questions
        print("start record questions")
        self.judge_results = await self.question_handler.record(self.questions)
        print("end record questions")
        judge_result_str = ""
        for judge_result in self.judge_results:
            judge_result_str += f"#{judge_result.question}\n"
            judge_result_str += f"Answer: {judge_result.answer}\n"
            judge_result_str += f"Correct Answer: {judge_result.correct_answer}\n"
            if judge_result.correct:
                judge_result_str += f"Correct: True\n"
            else:
                judge_result_str += f"Correct: False\n"
                judge_result_str += f"Error Reason(from LLM): {judge_result.error_reason}\n"
            judge_result_str += "\n"
            
        self.suggestion = judge_result_str
        print("judge_result_str", judge_result_str)
        record_agent = create_react_agent(
            model=self.model,
            tools=[
                make_search_resource_tool(),
                make_memory_add_tool(),
                make_memory_update_tool(),
                make_memory_delete_tool(),
                make_vocab_add_and_record_tool(),
                make_vocab_record_tool(),
                make_vocab_add_and_record_tool(),
                make_grammar_record_tool(),
                
            ],
            checkpointer=self.checkpointer
        )
        config = {"configurable": {"thread_id": "1"}}
        print("make payload")
        payload = {"messages": [
                {"role": "system", "content": f"""
你是“RecordAgent”（答题记录与学习画像更新Agent）。你的职责是对用户完成的一组题目（试卷）进行解析与归档，更新用户的长期/短期画像，并生成下一阶段学习建议。你不会生成题目；你只处理“已完成题目”的结果。

You Can:
1. 使用search_resource获取用户的信息
2. 使用add_memory工具增加目前已有的记忆, 使用update_memory工具修改目前已有的记忆, 使用delete_memory工具删除目前已有的记忆
3. add_and_record_vocab/add_and_record_grammar工具在用户的Grammar和Vocab(Vocabulary)表格里添加新的行, 这个工具会自动记录, 所以不需要再使用record_vocab/record_grammar工具
4. 在用户的Grammar/Vocab表里在已有行的情况下, 增加一次新的练习记录

Goal:
- 分析用户返回的每道题目的回答, 思考一下这道题目考察了什么
- 识别题目中使用到的**语法**与**词汇**, 并且在数据库中尝试搜索是否存在这个Vocab/Grammar的记录
- 如果不存在, 添加这个语法/词汇的Vocab/Grammar的新的行, 添加工具会自动记录, 所以不需要再使用record_vocab/record_grammar工具
- 在确认存在, 或者添加新的记录后, 根据用户正确或者错误的使用了语法或者词汇, 使用record_vocab/record_memory工具记录一次错误或者正确
- 完成记录后, 思考这道题目的新的答案是否相对之前的用户画像发生了变化, 如果发生了变化, 修改或者添加Memory


Constrains:
- 如果你想知道某个Vocab or Grammar是否在数据库中存在, 你应该用正则表达式查询, 这可以很轻易的查询这个Vocab or Grammar的所有Usage的变体, 来确认是否存在
- 如果你发现目前某个Vocab or Grammar的使用场景和数据库中已经存在的非常相似, 你应该直接使用已存在的而非新的
- Memory存在Summary和Content, Summary倾向于在非常简短的一句话内简述这个Memory的内容, Content倾向于记录这条Memory的细节
- Memory表完全由LLM, 也就是你维护, 所以在你添加或者修改Memory时, 必须和之前的风格相同

Tools:

- search_resouce
这个工具可以检索用户的信息

信息分以下几类
Memory:
- LLM根据用户对题目的回答, 聊天, 记录的用户画像, 这个表完全由LLM管理

Vocab&Grammar:
 - 这个表记录了用户对某个单词/语法的掌握程度
 - name代表这个单词或者语法的名称, 内部字段使用的是用户正在学习的语言记录的
 - usage代表这个单词或者语法的使用场景, 用于区分一个相同的语法的不同场景, 以及用于方便向量查询

Story:
- 这个表记录了用户自己写的一些关于自己的故事

Mistake:
- 这个表记录了用户的错题集

- add_and_record_vocab or add_and_record_grammar
这个工具会在vocab/grammar表中添加一条新的习得行, 并且设置为初始状态, 并且记录一次正确/错误
这个工具会自动记录, 所以不需要再使用record_vocab/record_grammar工具

- record_vocab or record_grammar
这个工具会给已有的行增加一次新的使用记录, 这个使用可以是正确使用或者错误使用

- add_memory
这会增加一条新的记忆

- update_memory
可以更改目前已有的记忆

- delete_memory
可以删除已有的记忆
"""},
                {"role": "system", "content": f"""
#User Info
- 这里记载了User在数据库中记录了多少信息, 如果你使用search_resource工具, 会在下方列出的信息内检索
{await self.memory_service.get_user_memory_count_prompt_for_agent()}
{await self.story_service.get_user_story_count_prompt_for_agent()}
{await self.mistake_service.get_user_mistake_count_prompt_for_agent()}
{await self.vocab_service.get_user_vocab_count_prompt_for_agent()}
{await self.grammar_service.get_user_grammar_count_prompt_for_agent()}
"""},
                {"role": "system", "content": f"""
{await self.memory_service.get_user_memory_summary_prompt_for_agent()}
"""},
                {"role": "system", "content": f"""
{await self.story_service.get_user_story_summary_prompt_for_agent()}
"""},
                {"role": "user", "content": judge_result_str},
            ]}
        print("start run_stream_events")
        await self.run_stream_events(
            agent=record_agent,
            payload=payload,
            config=config,
        )