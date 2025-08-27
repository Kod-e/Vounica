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
