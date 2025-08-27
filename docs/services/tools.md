# Tools (function / langchain)

ここは Agent が呼び出す **ツール置き場** です。  
私は実装を 2 層に分けました：

- `services/tools/function/`: 実際の処理（Service を呼ぶ）  
- `services/tools/langchain/`: ReAct Agent に渡す `StructuredTool` 定義（Args の型もここ）

共通の考え方はシンプルです：
- **UoW を前提**（`uow_ctx.get()`）にして、呼ぶ側は user_id を気にしない  
- **DB と Vector** は同じリクエストの中で一緒に扱う（Common Service 側で同期）  
- **AsyncSession の再入バグ回避** のために、**セッション単位の lock** をかける

---
## Memory & Vocab & Grammar Tools
ここは、Service層の関数をUoW（Unit of Work）付きでラップして、ReAct Agent用のツールとして公開しているだけです。特に難しいことはしていなくて、単純に既存のサービスをAgentから使いやすい形にしている感じです。
### 例 memory add tool
#### function 層
```python
# services/tools/function/memory.py
from app.infra.models.memory import Memory
from app.services.common.memory import MemoryService
from app.infra.context import uow_ctx
import asyncio, weakref
from sqlalchemy.ext.asyncio import AsyncSession

_session_locks = weakref.WeakKeyDictionary()

def _lock_for_session(session: AsyncSession) -> asyncio.Lock:
    lock = _session_locks.get(session)
    if lock is None:
        lock = asyncio.Lock()
        _session_locks[session] = lock
    return lock

async def add_memory(
    category: str,
    content: str,
    summary: str,
    priority: int = 0,
) -> str:
    session = uow_ctx.get().db
    async with _lock_for_session(session):
        memory: Memory = await MemoryService().create({
            "category": category,
            "content": content,
            "summary": summary,
            "language": uow_ctx.get().target_language,
            "priority": priority,
        })
    return f"""
memory added:
id: {memory.id}
summary: {summary}
category: {category}
content: {content}
priority: {priority}
updated_at: {memory.updated_at.isoformat()}
"""
```
#### memory: langchain 層（StructuredTool）
```python
# services/tools/langchain/memory.py（抜粋）
from ..function.memory import add_memory, update_memory, delete_memory
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class MemoryAddArgs(BaseModel):
    category: str = Field(..., description="メモリのカテゴリ。ツリー表示のために使います。")
    summary: str = Field(..., description="メモリの要約。できるだけ短く（最大 64 文字を想定）。")
    content: str = Field(..., description="メモリの本体。ユーザーの行動や事実を具体的に書いてください。")
    priority: int = Field(0, description="優先度。数字が大きいほど重要（デフォルト 0）。")

def make_memory_add_tool() -> StructuredTool:
    return StructuredTool.from_function(
        name="add_memory",
        coroutine=add_memory,
        description="""
メモリを1件DBに追加します。追加後は category ごとにツリーで整理され、
呼び出し時には summary も返します。
ユーザーにとって大事な情報だけを保存してください。短期の予定（例：今日の午後の予定）
のようなすぐ消える情報は入れないでください。
内容が古くなったら update_memory、不要になったら delete_memory を使い、
同じ内容を新規で作り直さないようにしてください。
""",
        args_schema=MemoryAddArgs,
    )
```

## Question Stack
(app/service/tools/langchain/question_stack.py)
これは Question Agent の“出題用の下書き（試験用の束）”です。  
Agent 初期化のときに作られて、**いくつかの設問をまとめて持つ**／**全部を文字列化して AI に渡す**ために使います。  
私は「問題を一回ここに積んでから出す」方が制御しやすいと思っています。

---

### 何をするの？

- `questions: List[QuestionUnion]` に設問をためる  
- 追加／削除／一覧を **LangChain の StructuredTool** で外から操作できる  
- 「全部の問題を 1 本の prompt 文字列」にして返す（Agent がそのまま読む）
- gather_tools は app/service/tools/langchain/question の下にある全部の .py Moduleをまわって、もしその中に build_tools 関数があれば拾ってまとめる、っていう仕組みです。

```python
from typing import List
from langchain_core.tools import StructuredTool
from app.infra.context import uow_ctx

class QuestionStack:
    def __init__(self):
        self.uow = uow_ctx.get()
        self.questions: List[QuestionUnion] = []

    # LangChain 側に渡すツールを集める（下の「プラグイン構造」を参照）
    def get_tools(self) -> List[StructuredTool]:
        from app.services.tools.langchain.question import gather_tools
        return gather_tools(self)

    # ---- 自分自身を操作するツール（例） ----

    def build_delete_question_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            name="delete_question",
            description="スタックから1問を削除します。削除後は後ろのindexが詰まります。",
            func=self.delete_question,
            args_schema=DeleteQuestionArgs,  # pydantic モデル
        )

    def build_get_questions_prompt_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            name="get_questions",
            description="現在の全設問を1つの multi-line prompt として返します。",
            func=self.get_questions_prompt,
            args_schema=EmptyArgs,  # 引数なしのダミーschema（{}で呼ぶ）
        )
```