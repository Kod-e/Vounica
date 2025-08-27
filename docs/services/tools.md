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