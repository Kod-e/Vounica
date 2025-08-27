# QuestionAgent

QuestionAgent は **ReAct** で動く出題用の Agent です。目的があるときに **tool call** を発火し、観察→思考→次の行動…をループします。私はこの流れが一番シンプルで、ログも追いやすいと思っています。

---

## なにをする

* ユーザーの最近の情報（Memory / Story / Vocab / Grammar / Mistake）を参考に、**次の問題**を作る
* 追加・削除・確認はすべて **QuestionStack** を通して行う（最後にまとめて配布）
* 必要な詳細は **search\_resource** などのツールで都度とりにいく（最初はサマリだけ）

---

## ReAct 実行（LangGraph）

QuestionAgent は `langgraph.create_react_agent` を使って ReAct を回します。
自分で ReAct の制御を書く必要はなく、LangGraph がイベント単位で面倒を見てくれます。

```python
# 1) Agent を作成
question_agent = create_react_agent(
    model=self.model,
    tools=[
        make_search_resource_tool(),
        self.question_stack.build_delete_question_tool(),
        self.question_stack.build_get_questions_prompt_tool(),
        *self.question_stack.get_tools(),  # add_*_question 系
    ],
    checkpointer=self.checkpointer,
)

# 2) 実行ペイロード
config = {"configurable": {"thread_id": "1"}}
payload = {"messages": messages}  # 下の System Message を含む

# 3) 実行（CoreAgent が stream へ橋渡し）
await self.run_stream_events(agent=question_agent, payload=payload, config=config)
```

---

## 初期コンテキスト（System Message）

最初に **System Message** で「件数サマリ→短い要約→直近の学習記録」を渡します。
ここが QuestionAgent の **軽い記憶** です。深い検索は必要になってから tool で行います。

```python
# 件数（まず“どの領域に何件あるか”を宣言）
{"role": "system", "content": f"""
# User Info
{await self.memory_service.get_user_memory_count_prompt_for_agent()}
{await self.story_service.get_user_story_count_prompt_for_agent()}
{await self.mistake_service.get_user_mistake_count_prompt_for_agent()}
{await self.vocab_service.get_user_vocab_count_prompt_for_agent()}
{await self.grammar_service.get_user_grammar_count_prompt_for_agent()}
"""}

# 要約（AI がすぐ掴める短いサマリ）
{"role": "system", "content": f"{await self.memory_service.get_user_memory_summary_prompt_for_agent()}"}
{"role": "system", "content": f"{await self.story_service.get_user_story_summary_prompt_for_agent()}"}

# 最近の記録（直近のみ）
{"role": "system", "content": f"{await self.vocab_service.get_recent_vocab_prompt_for_agent()}"}
{"role": "system", "content": f"{await self.grammar_service.get_recent_grammar_prompt_for_agent()}"}
{"role": "system", "content": f"{await self.mistake_service.get_user_mistake_prompt_for_agent()}"}
```

私は「最初は軽く、必要なときに tool で掘る」方針が、無駄がなくて好きです。

---

## 使用Tool

* **search\_resource**：ユーザー情報を検索（Memory / Vocab / Grammar / Story / Mistake）
* **get\_questions**：現在の QuestionStack を確認（multi-line の文字列）
* **delete\_question**：不正な問題を取り除く（規則に違反するもの）
* **add\_\*\_question**：各形式の問題を追加（`add_choice_question` など）

> QuestionStack 下のツールはプラグイン式で収集（`gather_tools`）。増やすのが簡単です。

---

## 出題フロー

1. System Message に件数・要約・直近記録を入れて **messages** を構成
2. ReAct を開始（LangGraph）
3. 必要に応じて **add\_\*\_question** で QuestionStack へ追加
4. **get\_questions** で全体を確認
5. 規則に合わないものがあれば **delete\_question**
6. まとまったら終了。Stack の中身が **最終の出題** になります

私はこの“追加→確認→修正”の回し方が、一番ミスが少ないと感じています。

---

## 制約

* 出題は **target\_language** と **accept\_language** の二言語内に限定
* **正答の漏えい禁止**（`correct_answer` 以外に出さない）
* **唯一解** と **正確性** を守る
* 初心者は母語の設問、高度になれば target での設問も可

（詳細は Agent 側の System Prompt の *QuestionRules* を参照）

---

## 終了と結果

CoreAgent の `run_stream_events` が **AgentEvent** に変換して前端へ流します。
最後は `get_questions` で確認した **QuestionStack** の内容をそのまま返します。

私はこの分離（CoreAgent = 配信基盤 / QuestionAgent = 出題方針）が、実装と運用の両方でわかりやすいと思います。
