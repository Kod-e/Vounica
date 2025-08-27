# RecordAgent
(app/service/agent/record/agent.py)
RecordAgent は **採点・記録** を担当する Agent です。動きは QuestionAgent と同じく **ReAct**。目的があるときに **tool call** を発火し、観察→思考→次の行動…をループします。私はこの分離（出題＝Question / 記録＝Record）が一番わかりやすいと思いました。

---

## 役割（なにをする？）

* ユーザーの回答を **judge** して結果をまとめる（`JudgeResult[]`）
* Vocab / Grammar の **存在確認・追加・記録** を行う
* Memory の **作成・更新・削除** を必要なぶんだけ行う
* 仕上げに **学習の提案（suggestion）** を作って返す

最初に **System Message** で「件数サマリ → 短い要約 → 最近の記録」を入れます。深いデータは必要な時に `search_resource` で取りに行く方針です。

---

## 実行フロー（二段構成）

RecordAgent は大きく **Phase 1（Vocab/Grammar）** → **Phase 2（Memory）** の二段で回します。どちらも `CoreAgent.run_stream_events(...)` で **イベントを逐次送出**します。

### Phase 1: Vocab / Grammar pass

1. まず `QuestionHandler.record(questions)` で全問を **judge**（結果は `judge_results` として保持）
2. `judge_results` から短いテキスト（どの問題に正誤・理由）を組み立て、**user message** に渡す
3. **tools** は次を使用：

   * `search_resource`
   * `add_and_record_vocab`, `record_vocab`
   * `add_and_record_grammar`, `record_grammar`
4. 目的：**足りない語彙や文法を追加**し、すでにあるものは **練習記録（正誤）を追記**する

> 既存と似すぎる usage は再利用、重複作成は避ける…などの制約は System Message に書いて強制します。

### Phase 2: Memory pass

1. Memory の定義（Summary/Content/Category）と運用ルールを **System Message** に明示
2. **tools** は次を使用：

   * `search_resource`
   * `add_memory`, `update_memory`, `delete_memory`
3. 目的：今回の回答から **ユーザー像の変化** を反映する（新規作成 or 更新 or skip）
4. Summary は **≤ 64**、Category は **大分類（最大 6 程度）** を守る

> 私は「まず軽い記憶を渡して、必要なときに tool で深掘り」の方が無駄が少ないと感じます。

---

## Suggestion（提案の生成）

最後に小さな tool（`set_suggestion`）をひとつ用意して、Agent に **短い提案文** を作らせます。これも ReAct で回し、`AgentEvent` として前端へ流します。

```python
# イメージ（抜粋）
tool = StructuredTool.from_function(name="set_suggestion", coroutine=self.set_suggestion, args_schema=SetSuggestionArgs)
agent = create_react_agent(model=self.model, tools=[tool], checkpointer=self.checkpointer)
await self.run_stream_events(agent, payload, config)
```

---

## 初期コンテキスト（System Message 例）

* 件数：Memory / Story / Vocab / Grammar / Mistake の **count** を列挙
* 要約：Memory と Story の **summary** を渡す
* 最近：Vocab / Grammar / Mistake の **最近データ** を渡す
* user 入力：`judge_results` を整形した **回答サマリ** を渡す

この「軽い記憶＋最近ログ」で出発し、深い検索は `search_resource` で必要時に行います。

---

## 使用ツール（まとめ）

**Phase 1**

* `search_resource`
* `add_and_record_vocab`, `record_vocab`
* `add_and_record_grammar`, `record_grammar`

**Phase 2**

* `search_resource`
* `add_memory`, `update_memory`, `delete_memory`

**Suggestion**

* `set_suggestion`

---

## Streaming と Event

`CoreAgent` の **message queue** をそのまま使います。`run_stream_events(...)` が LangGraph の生イベントを `AgentEvent`（thinking / stream\_chunk / stream\_end / tool\_call / result）に写像し、**WebSocket / StreamingResponse** 経由で前端に届きます。

---

## 安全と一貫性

* すべての tool は **UoW（uow\_ctx）** に依存。**ユーザーごとに資源が分離**され、権限越えが起きません
* DB と Vector は **同じ request 文脈**で扱われ、片方だけ成功する不一致を防止
* 例外時は **rollback**、stream は **end event** を送って確実に閉じます

---

## 最終出力

最終的に `RecordAgentResultEvent` を送ります：

* `suggestion`: 改善の方向を短く
* `judge_results`: 各設問の正誤と理由（必要なら）

私はこの二段構成（Vocab/Grammar → Memory）にしてから、後処理の抜け漏れが減りました。実装も読みやすく、運用もしやすいです。
