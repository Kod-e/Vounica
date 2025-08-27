# API V1
(app/api/v1)
ここは **FastAPI** の API レイヤーです。ルートは **/api/v1**。  
基本はシンプルにしていて、私は「infra で定義した型をそのまま使う」方針にしています。

## 方針
- **Schema**：request / response は **infra の Pydantic schema** をそのまま使います。  
  → OpenAPI にも同じ定義が出るので、**Vue** からは自動生成タイプでそのまま使えて、二重定義がいりません。
- **認証**：`Authorization: Bearer <JWT>`。  
  さらに `Accept-Language` / `Target-Language` をヘッダで受け取り、**UoW** にまとめます。
- **依存注入 (DI)**：auth 以外のルートは **UoW を Depends** で注入。  
  → `db` と `qdrant (vector)` を **同じリクエスト文脈**で扱い、最後に **commit / rollback** を一括。  
  → 呼び出し側は **user_id を意識しない CRUD**（Service が UoW 経由で解決）。

## Agent ルート
- **WebSocket push** で進捗をリアルタイム送出（CoreAgent の **queue → event** 方式）。  
- WS 用には **専用の UoW（get_uow_ws）** を用意。token / language を header or query から拾って、  
  リクエスト中は **ContextVar** で隔離（越権を防止）。

## Streaming について（メモ）
- FastAPI **0.105** の更新以降、**SSE** で早期に `aclose` が走る事象に当たりました。  
  そのため、今は **WS が正式**。SSE の試作コードは一部 **残骸**として残っています（将来の検証用）。

## まとめ
- **/api/v1** に集約、**infra の schema** を OpenAPI 経由で前後共通化。  
- 依存は **UoW 一箇所**にまとめ、DB と Vector を **同時に安全**に扱う。  
- Agent は **WS で push**、UI はそのまま event を読んで画面更新。  
私はこの構成が、実装も運用もいちばん手堅いと感じています。