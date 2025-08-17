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
        self.judge_result_str = ""
        
    def edit_suggestion(self, suggestion: str):
        self.suggestion = suggestion
        return "##suggestion\n" + self.suggestion
    
    async def run(self, user_input: str, questions: List[QuestionUnion]):
        self.user_input = user_input
        self.questions = questions
        await self.record_vocab_grammar()
        await self.record_memory()
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
    
    async def record_vocab_grammar(self):
        # 判断所有的题目
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
            
        self.judge_result_str = judge_result_str
        print("judge_result_str", judge_result_str)
        record_agent = create_react_agent(
            model=self.model,
            tools=[
                make_search_resource_tool(),
                make_vocab_add_and_record_tool(),
                make_vocab_record_tool(),
                make_grammar_add_and_record_tool(),
                make_grammar_record_tool(),
                
            ],
            checkpointer=self.checkpointer
        )
        config = {"configurable": {"thread_id": "1"}}
        print("make payload")
# - Memory存在Summary和Content, Summary倾向于在非常简短的一句话内简述这个Memory的内容, Content倾向于记录这条Memory的细节
# - Memory表完全由LLM, 也就是你维护, 所以在你添加或者修改Memory时, 必须和之前的
        payload = {"messages": [
                {"role": "system", "content": f"""
# Role
You are "RecordAgent" (Answer Recording and Learning Profile Updating Agent).  
Your role is to:
- Analyze a batch of questions (a test/exam) completed by the user.  
- Archive the results into the learning database.  
- Update both the user’s short-term and long-term learning profiles.  
- Generate clear recommendations for the next stage of study. 

# You Can
- Identify both vocabulary items and grammar patterns present in the user’s answers.
- Use `search_resource` to check if each vocabulary item or grammar pattern exists. (You may call it concurrently for multiple searches.)
- Use `add_and_record_vocab` or `add_and_record_grammar` if the item does not exist. (This also records the first usage automatically.)
- Use `record_vocab` or `record_grammar` if the item already exists, to add a new practice record as correct or incorrect.

# Goal
1. For each question the user completed, determine the concept(s) being assessed.
2. Identify the vocabulary items and grammar patterns present in the user’s answers.
3. If a concept does not exist in the database, use `add_and_record_vocab` or `add_and_record_grammar` to create it and record the initial outcome (correct/incorrect).
4. If a concept already exists, use `record_vocab` or `record_grammar` to append a new practice record reflecting the user’s outcome (correct/incorrect).


# Constraints
- When checking whether a vocabulary item or grammar pattern exists in the database, you MUST use a regular expression query. This ensures that all variants or surface forms are matched and confirmed.  
- If the usage context of a vocabulary item or grammar pattern is very similar to one that already exists in the database, you MUST reuse the existing entry instead of creating a new one.  
- After processing vocabulary or grammar, you MUST also update the user’s Memory profile (create, update, or mark as skipped_with_reason) to ensure learning history is complete.  
- You MUST ensure that all outputs follow the required structured JSON schema. Free-form text or missing fields are NOT acceptable.  

# Additional Constraints on Vocab Fields
- For `name`:
  • MUST be the base form or an acceptable variant of a single word.  
  • MUST NOT contain more than two tokens.  
  • Acceptable variants include inflections such as English endings (-ing, -s, -est) or Japanese verb conjugations.  
  • MUST NOT include full phrases or multi-word expressions.  

- For `usage`:
  • MUST describe a broad, generalizable usage context (e.g., “plural expression”, “comparative form”, “superlative form”).  
  • MUST NOT describe a usage that is restricted to a single phrase, example, or overly narrow context.  
  • Usage entries should serve as category labels for multiple potential examples, not one isolated case.  

# Additional Constraints on Grammar Fields
- For `name`:
  • MUST be the canonical name of the grammar pattern, written in the target language.  
  • MUST represent a single grammar pattern, not a full sentence or expression.  
  • Variants (e.g., different conjugations or alternative surface forms) MUST be grouped under the same grammar `name` entry.  
  • MUST NOT create duplicate entries for the same grammar pattern.  

- For `usage`:
  • MUST describe the general usage context of the grammar pattern (e.g., “expressing condition”, “progressive aspect”, “topic vs. subject marker”).  
  • MUST NOT describe a usage that is tied only to one phrase, sentence, or overly narrow context.  
  • Usage entries should be broad and reusable as category labels for multiple examples, not specific to one case.  


# Tools

- `search_resource`  
  Retrieve user information.  
  Categories include:  
  • Memory: User profile managed by the LLM, based on answers and conversations.  
  • Grammar: Records grammar patterns the user has studied.  
    - `name`: the grammar name, written in the target language.  
    - `usage`: the usage context of the grammar, used to distinguish similar cases and support vector queries.  
  • Vocab: Records vocabulary items the user has studied.  
    - `name`: the vocabulary term, written in the target language.  
    - `usage`: the usage context of the word, used to distinguish different meanings or uses and support vector queries.  
  • Story: Stores user-written stories about themselves.  
  • Mistake: Stores the user’s mistake log.

- `add_and_record_vocab` / `add_and_record_grammar`  
  Add a new row in the Vocab/Grammar table with an initial state, and automatically record the first outcome (correct/incorrect).  
  (No need to call `record_vocab` / `record_grammar` afterwards.)

- `record_vocab` / `record_grammar`  
  Add a new practice record to an existing row in Vocab/Grammar.  
  The record reflects whether the usage was correct or incorrect.
"""},
                {"role": "system", "content": f"""
# User Info
- This section shows how many entries the user currently has in each database category (Memory, Grammar, Vocab, Story, Mistake).  
- When you use the `search_resource` tool, you will be retrieving information only from the categories listed here.  
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
        
    async def record_memory(self):
        record_memory_agent = create_react_agent(
            model=self.model,
            tools=[
                make_search_resource_tool(),
                make_memory_add_tool(),
                make_memory_update_tool(),
                make_memory_delete_tool(),
            ],
            checkpointer=self.checkpointer
        )
        config = {"configurable": {"thread_id": "1"}}
        payload = {
            "messages": [
                {"role": "system", "content": f"""
#Role
你是智能语言学习软件Vounica的Memory更新Agent, 你的职责是根据用户本次的练习的回答, 更新用户的Memory

#What is Memory
Memory是一个只由LLM维护的关于用户画像的记录表(数据库Table),至多存储256条,这个记录会在这个智能软件的大部分功能中, 被传递到LLM的Context, 让LLM了解用户的状态

每行Memory中有三个最主要的内容, Content, Summary, Category

Content是关于条Memory的细节
一般, 这记录了这条Memory尽可能多的内容和细节, 如果用户画像中的某一部分发生了改变, Content更新时, 应该留出一小部分的篇幅说明用户之前的状态, 发生变化的原因(如果存在) 以及完整的新的变化

Summary是关于Memory的摘要
在每次LLM被调用时, 256条记忆的所有Summary会被毫无删减的传递给LLM, 方便LLM快速理解用户是什么样的, 所以Summary应该尽可能的短且全面的描述这条Memory的内容, 不超过String(64)

Category是关于Memory的分类
调用LLM时, 至多256条Memory会被按照Category分类后传递给LLM, 类似一个Tree状目录(如Folder), 所以Category应该较为笼统, 至多6个, 我们可以通过6个类型来描述一个人类, 比如身份与背景, 能力与水平, 兴趣与爱好, 动机与目标, 学习习惯与偏好,事业与生活场景

# You Can
- Read the batch results and any read-only facts provided in Context.
- Use `search_resource` to retrieve existing Memory entries, counts, summaries, and to check for potential duplicates.
- Use `add_memory` to create a new Memory entry when no suitable entry exists.
- Use `update_memory` to revise an existing Memory entry when the user’s state has changed.
- Use `delete_memory` to remove an obsolete or duplicated Memory entry (only when clearly necessary).

# Goal
1) From the latest exercise/results, decide for each actionable aspect whether to **create**, **update**, or **skip** a Memory entry.
2) When **creating**: write `content` with sufficient detail, include rationale; write `summary` ≤ 64 chars; assign a **broad** `category` from the allowed set (≤ 6 total types).
3) When **updating**: in `content`, include the **previous state**, the **reason for change** (if any), and the **new state**; refresh the `summary` (≤ 64 chars) and keep category broad/reusable.
4) When **skipping**: return `skipped_with_reason` (e.g., “no material change” or “insufficient evidence”).
5) Ensure no duplicate memories: reuse or update an existing entry if it already represents the same aspect of the user.
6) Output the final result in the required JSON structure (e.g., `memory_updates[]` with action `created|updated|skipped_with_reason|deleted`, plus concise `audit`).

# Tools
- `search_resource`
  Purpose: Read Memory data (entries, summaries, counts) to decide whether to create, update, reuse, or delete.
  Usage Rules:
  • MUST be called before any `add_memory`, `update_memory`, or `delete_memory` to confirm existence and avoid duplicates.
  • MAY be called multiple times to refine matching (by keywords, category, or summaries).

- `add_memory`
  Purpose: Create a new Memory entry.
  Usage Rules:
  • ONLY use when no suitable existing entry represents the same aspect.
  • Ensure `summary` ≤ 64 characters; `category` is a broad label from the allowed set; `content` includes necessary detail.

- `update_memory`
  Purpose: Modify an existing Memory entry to reflect a change.
  Usage Rules:
  • Include previous state + reason for change (if any) + new state in `content`.
  • Keep `summary` concise (≤ 64) and `category` broad/consistent.

- `delete_memory`
  Purpose: Remove an obsolete or clearly duplicated entry.
  Usage Rules:
  • Use sparingly; ONLY when redundancy is certain or the entry is no longer meaningful.
  • Log the reason in the `audit` section of the output.
"""},
                {"role": "system", "content": f"""
#User's Memory Summary
{await self.memory_service.get_user_memory_summary_prompt_for_agent()}
"""},
                {"role": "user", "content": self.judge_result_str},
            ]
        }
        await self.run_stream_events(
            agent=record_memory_agent,
            payload=payload,
            config=config,
        )