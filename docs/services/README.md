# Service層 README

Service層は、このプロジェクトの「実際に何をするか」をまとめた部分です。  
Infra がデータを保存・取得するだけなら、Service はそれを組み合わせて「機能」に変える。  
私はここを「アプリのあたま」に近い層だと思っています。


## Common Service
(app/service/common)
Common は「Repo を使いやすくする小さなサービス」です。  
私はここで **Unit of Work (UoW)** を前提にして、**ユーザーIDを意識しない CRUD** を実現しました。  
つまり、呼び出す側は毎回 `user_id` を渡さなくても、**現在のユーザーの文脈**で安全に操作できます。

### BaseService（共通のCRUD + Vector 同期）

`app/services/common/common_base.py` にある `BaseService` は、Repository をラップして次のことをします：

- **UoW の自動取得**：`uow_ctx.get()` で現在のリクエストの UoW を掴む  
- **ユーザー自動紐づけ**：`create()` で `user_id` が無ければ `uow.current_user_id` を補完  
- **Vector 同期**：保存や更新のたびに `queue_vector_from_instance(...)` を呼び、**同一トランザクション内**で Qdrant へも反映

```python
class BaseService(Generic[T]):
    def __init__(self, repository: Repository[T]):
        self._repo: Repository[T] = repository
        self._uow = uow_ctx.get()  # UoW を現在のコンテキストから取得

    async def create(self, data: Dict[str, Any]) -> T:  # type: ignore[type-var]
        if "user_id" not in data:
            data["user_id"] = self._uow.current_user_id  # 呼び出し側は user_id を気にしない
        instance: T = await self._repo.create(self._uow.db, data)
        queue_vector_from_instance(instance, self._uow.vector)  # ← 同期して Vector も更新
        return instance
```

### StoryService（具体的な例）

`StoryService` は `BaseService` を継承し、ユーザーのストーリーに関する操作を封装したサービスです。  
UoW を利用しており、`create` メソッドでは自動的にユーザーIDを補完し、さらに Qdrant にも同期されます。  
これにより、ストーリーの作成や取得が簡単かつ安全に行えます。

```python
class StoryService(BaseService[Story]):
    def __init__(self, repository: Repository[Story]):
        super().__init__(repository)

    async def get_user_stories(self) -> List[Story]:
        user_id = self._uow.current_user_id
        return await self._repo.filter_by_user_id(self._uow.db, user_id)
```

## Auth Service
(app/service/auth)
Auth Service は ユーザー認証まわり をまとめています。
register / login / refresh / guest などを一つの class にして、内部では UserRepository と RefreshTokenRepository を使います。
- register：新しいユーザーを作成する。すでに同じメールがあるとエラー。
- guest：一時的なGuestユーザーを自動生成して、token を返す。
- login：メールとパスワードをチェックして、正しい場合に token を返す。
- refresh：refresh token を確認して、新しい access token を返す。
私は Auth Service を使うことで、FastAPI の handler がシンプルになり、認証ロジックを一か所で管理できるのが便利だと思いました。

- [tools.md](tools.md)  
  ここは Agent が呼び出す **ツール置き場** です。  
  `function` のほうは「Agent が Call できる関数の型」を定義していて、必要なら UoW を注入した wrapper をかけます。  
  `langchain` のほうは ReAct Agent にそのまま渡せる tools を並べていて、Args はどう受けるかをちゃんと決めています。  

- [question.md](question.md)  
  Question の基本型 (`QuestionSpec`) を定義しました。  
  SwiftUI を書いたときの発想に近くて、「protocol っぽい」書き方で、Choice / Match / Assembly とかを増やしても自然に拡張できます。  

- [agent.md](agent.md)  
  Agent の本体。CoreAgent がベースで、Event push とか init の共通処理をまとめています。  
  そこから QuestionAgent と RecordAgent を作って、学習ループを回しています。  
  正直、ここが一番「動いてる感」があって、作ってて面白かったところです。  