# Infra層 README

このREADMEは、Infra層について説明します。Infra層はCore層の上にあり、Database Model、Repository、Schemaなどをまとめて、Service層にデータアクセスを提供します。


## 役割

Infra層の主な役割は、Core層のModelやUseCaseと連携し、実際のデータベースや外部サービスへのアクセス処理をまとめることです。  
Service層は、Infra層を通じてデータを取得・保存します。

例えば、Infra層は次のものを管理します:
- Database Model（DBのテーブル定義）
- Repository（データアクセスの実装）
- Schema（データの変換や検証）
- 外部サービス連携（Qdrant, Redisなど）

---

## Database Model（Story）

Database Model は DB のテーブルやレコードを Python クラスで表現したものです。
このプロジェクトでは SQLAlchemy を使っています。

例えば Storyテーブルは、ユーザーの日記や出来事を保存します。
Story は BaseModel を継承していて、created_at と updated_at が自動で付きます。
私はこういう共通フィールドを Base にまとめる設計は、とても便利だと思いました。

```python
# 故事表, ユーザーのストーリーを記録します
class Story(BaseModel):
    """
    The Story table by SQLAlchemy.
    これはStory Tableです。
    """
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # ストーリー本文 (GPT が生成する内容, vector化されます)
    content = Column(Text)
    
    # ストーリーの要約 (LLM が生成, ユーザーの好みを把握するために使う, vector化されます)
    summary = Column(Text)
    
    # ストーリーのカテゴリ (Tree構造ディレクトリ, ユーザー定義。defaultは "default")
    # GPT は入力されたストーリーをもとに、既存カテゴリとの関連を提案します。
    category = Column(String(32))

    # ストーリーの言語 (ISO 639-1 code, 例: "ja", "en", "zh")
    language = Column(String(8), default="zh")
```

---

## Repository (Story)

Repository は Core の Base Repository を継承しています。  
そのため `get_by_id`, `create`, `update`, `delete` ... などの基本操作は全部自動で使えます。  
さらに Infra 側で「よく使う ORM クエリ」をメソッドにまとめ、外部から便利に呼び出せるようにしました。  
私はこういう形でクエリをカプセル化すると、Service 層のコードがすごく読みやすくなると思います。

例えば StoryRepositoryは、ユーザーの最近のストーリーを簡単に取得できます。
```python
#app/infra/repo/story_repository.py
class StoryRepository(Repository[Story]):
    """Repository class for Story model.
    これは Story model用(よう)の repository 基本(きほん) classです。
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Story)
        self.db = db 

    # ユーザーのストーリーを取得する関数
    async def get_user_stories(
        self, user_id: int, offset: int = 0, limit: int = 100, language: str | None = None
    ) -> List[Story]:
        """Get the user's stories."""
        query = select(Story).where(Story.user_id == user_id)
        if language:
            query = query.where(Story.language == language)
        stories = await self.db.execute(query.offset(offset).limit(limit))
        return stories.scalars().all()
```

## Quota (Token制限)

QuotaBucket は app/infra/quota/bucket.py にあります。
Redis を使って User ごとの 消費バケツ (consumption bucket) を作ります。
Bucket には window (有効期限) があり、時間が過ぎると自動で reset されます。
私はこの仕組みで「使いすぎ防止」と「公平性」がシンプルにできると思いました。


## Schema

FastAPI で使う Schema は全部 app/infra/schemas/ に置いています。
例えば RegisterSchema, LoginSchema, TokenSchema などです。
User, Story, Memory, Vocab, Grammar, Mistake など全部に対応する Schema があり、
Pydantic で入力チェックと出力整形をしています。

私は Schema を infra にまとめることで、API 層と Service 層の両方から再利用できて便利だと思いました。

## Vector (Qdrant)
(app/infra/vector)
AI Agent が 意味検索 をできるようにすると、プロジェクト全体の効率がすごく高くなります。
例えば「食べ物」で検索すると、リンゴ・ラーメン・寿司 まで一緒に見つけられる。
そのため、このプロジェクトでは Memory, Grammar, Vocab, Mistake, Story などを Qdrant の collection に分けて保存しています。

現在は OpenAI の embedding model を使ってベクトル化しています。
正直に言うとオープンソースやクローズドの選択肢はいろいろありますが、便利さのために OpenAI を選びました。


## Unit of Work (UoW)

FastAPI には 依存注入 (Dependency Injection) の仕組みがあります。
このプロジェクトでは、UnitOfWork を作って DB / Vector(Qdrant) / Redis / User 情報 を まとめて一回で注入 できるようにしました。

普通の ORM (SQLAlchemy) には transaction があって commit / rollback ができますが、Qdrant には transaction がありません。
そこで UoW で2つを同時に扱う仕組みを作り、最後に commit() か rollback() を呼ぶと DB と Qdrant が同じ状態になるようにしています。

さらに Core の JWT 認証処理 もここに統合しています。
だから API handler では uow を一度受け取れば、request 全体で次のものにアクセスできます：
- uow.db (SQLAlchemy Session)
- uow.vector (Qdrant の VectorSession)
- uow.redis (Redis Client)
- uow.current_user (JWT から解決した User 情報)
- uow.quota (Token QuotaBucket)

また、uow_ctx という ContextVar を使っているので、request の途中のどこからでも今の UoW にアクセス可能です。
これは Agent の tool call にも役立ちます。
例えば prompt injection 攻撃で「別のユーザーの情報を見せて」と言われても、uow_ctx がユーザーごとに隔離されているので越権アクセスはできません。

私はこの設計のおかげで 「一回依存を渡すだけで全部安全に使える」 のがとても便利だと思いました。