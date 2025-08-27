# Agent

Agent は **ReAct 方式** で動きます。目的があるときに tool call を発火し、観察→思考→次の行動…を **ループ** します。ゴールに到達したら終了

---

## ReAct の流れ
- 目的を設定（例：ユーザーの最近の学習ログから次の問題を作る）
- 思考（reasoning）
- 必要なら **tool call**（memory / vocab / grammar / search / question_stack など）
- 観察（observation）
- 次の思考…を **繰り返す**
- 終了条件を満たしたら **result** を返す

---

## CoreAgent（共通の土台）
私の実装では、すべての Agent は `CoreAgent` を土台にしています。

- **UoW と model**：`uow_ctx` から現在のユーザー文脈を取り、`ChatOpenAI` を3種（high/standard/low）で用意
- **message queue**：`asyncio.Queue`。Agent の内部イベントをここに積み、外部は逐次読み出す
- **checkpointer**：`InMemorySaver`（LangGraph の簡易 checkpoint）
- **run() 抽象**：各サブクラスは `run(*args) -> BaseModel` を実装（結果は **Pydantic** オブジェクト）
- **push API**：`finish() / message() / event()` で `AgentEvent` を queue に投入

> 具体的な派生：`QuestionAgent` / `RecordAgent` など。

---

## Streaming（外部へ逐次送出）
**外側からは stream として読むだけ**で進捗が取れます。

- `run_stream(*args)`：内部で `run()` を並行実行しつつ、queue から `AgentEvent` を **yield**。`RESULT` を受けたら終了
- FastAPI の `StreamingResponse` と相性がよく、**WebSocket** でもそのまま流せます

簡単なイメージ：
```python
# 外側（FastAPIなど）
async def stream(agent: react_agent, *args):
    async for ev in agent.run_stream(*args):
        yield ev  # そのままフロントへ送る（JSON化）
```

---

## LangGraph 連携（astream_events の橋渡し）
`run_stream_events(agent, payload, config)` で **LangGraph** の生イベントを、こちらの `AgentEvent` に写像します。

- `on_chat_model_start` → `AgentThinkingEvent`
- `on_chat_model_stream` → `AgentStreamChunkEvent`（chunk.content を逐次送出）
- `on_chat_model_end` → `AgentStreamEndEvent`
- `on_tool_end` → `AgentToolCallEvent`（tool 名と data を添付）
- `on_chain_end (LangGraph)` → ループを抜ける
- 例外時：`AgentStreamEndEvent` を送り、安全に停止

これにより、**model 出力**・**tool 呼び出し**・**終了**が前端にリアルタイム伝播します。

---

## Event 種別（概要）
最小でも次があれば十分だと思います。

- `AgentThinkingEvent`：モデルが考えている合図
- `AgentStreamChunkEvent`：文章の **chunk** を逐次送出
- `AgentStreamEndEvent`：chunk の終了
- `AgentToolCallEvent`：どの **tool** をどう呼んだかの記録
- `AgentResultEvent`：最終結果（`BaseModel` 派生で受け取る）
- `AgentMessageEvent`：任意メッセージ（UI 向けの通知など）

---

## WebSocket 配信
message queue で **生産（Agent）** と **消費（外部）** を分離しています。  
前端は queue から出てくる `AgentEvent` を順番に受け取り、画面を更新するだけ。  
私はこの形が一番バグを追いやすいと感じました。

---

## 安全と一貫性
- すべての tool は **UoW** に依存（`uow_ctx`）。**ユーザーごとに資源が分離**され、**権限越え**が起きません
- DB と Vector の操作は **同じ request 文脈**で扱われ、片方だけ成功する不一致を避けます
- 例外時は **rollback**、stream は **end event** を送って確実に閉じる

---

## まとめ
- Agent は **ReAct で目的達成までループ**
- `CoreAgent` は **queue + stream + event** の土台を提供
- LangGraph のイベントを **自前の AgentEvent** に写像して、前端に逐次伝える
- UoW によって **安全** と **一貫性** を担保

私はこの構成が「実装が見通しやすく、運用も楽」だと思っています。


## QuestionAgent
- [question_agent.md](question_agent.md)  
  Question Agent の本体

## RecordAgent
- [record_agent.md](record_agent.md)  
  Record Agent の本体