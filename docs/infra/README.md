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