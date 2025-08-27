# Vounica プロジェクト概要

> 名前の後半「unica」は Latin 語から来ました。前半の「vo」は voice（声）、vocabulary（単語）などの意味を考えられます。  
> 全体の意味は「一人一人に unique な language learning コースを作る」です。


## Install と　Access

## Demo
https://vounica.com

### 1. リポジトリを clone
```bash
git clone https://github.com/Kod-e/Vounica.git
cd Vounica
```
### 2. 環境変数を作成
```bash
cp .example.env .env
cp .example.docker.env .docker.env
```
.env と .docker.env をコピーしたあと、OPENAI_API_KEY, JWT_PRIVATE_KEY_B64, JWT_PUBLIC_KEY_B64 など未記入の値を必ず設定してください。
JWT鍵は ES256 (ECDSA P-256) を PEM形式で生成し、Base64 に変換して入れます。
### 3. Docker Compose で起動（おすすめ）
```bash
docker compose up -d --build
```
### 4. Access
APIとVue Dist: http://localhost:8000/

## 使用している技術

### backend：Python + Fa stAPI + SQLAlchemy + Qdrant

- Python は library が多く、とても便利です。  
- ORM, Qdrant SDK, OpenAI SDK, LangChain などを使っています。  
- 性能の問題は Python 自体より、設計や database に出ると思います。

### frontend：Vue 3 + Pinia + OpenAPI Fetch

- この GitHub repo には backend の code だけです。frontend は別 repo（https://github.com/Kod-e/Vounica-Web）にあります。  
- Vue3 + Pinia を使うと、UI は data を管理せず、ただ表示するだけです。imperative な code はほとんど不要です。  
- backend の FastAPI が出す OpenAPI schema をそのまま使えるので、frontend で model を作り直す必要はありません。


## プロジェクト構成

本プロジェクトの backend は **Core → Infra → Service → API** の4層構造で作られています。  
すべて async 対応の code で書かれており、保守しやすいように設計しました。  
詳しい内容は docs/ 以下のファイルをご覧ください。

- [docs/core/README.md](docs/core/README.md)  
  基本的な定義をまとめる層。  
  例：DB SessionMaker の取得方法、Qdrant client、JWT の作成、アプリ起動時に必要な初期化など。  

- [docs/infra/README.md](docs/infra/README.md)  
  database model の定義、関連する schema、vector collection の定義を行います。  
  また repo (repository) を通して model を操作し、もし semantic search が必要な field があれば vector DB にも同時に保存します。  
  特に **Unit of Work (UoW)** が重要で、FastAPI の request ごとに Session と user 情報をまとめて提供します。ContextVar に保存され、request 中ならどこからでも参照できます。  
  さらに Qdrant には transaction がないため、UoW 内に仮想 transaction 機構を作り、一時的に Qdrant の操作を cache し、最後に ORM と同時に commit することで不整合を防ぎます。  

- [docs/services/README.md](docs/services/README.md)  
  実際のビジネスロジックを実装する層。  
  Agent, Question, Record などを中心に機能がまとまっており、詳細は専用ページで説明します。  

- [docs/api/README.md](docs/api/README.md)  
  Infra 層の schema を利用して Service の機能を呼び出す FastAPI endpoint を提供する層。  
  エンドポイント定義や依存解決が含まれます。  

### Question → Record → Question のループ

Vounica の特徴は、Question（問題を出す）→ Record（答えや間違いを記録する）→ Question（次の問題を出す）というサイクルです。このサイクルは Agent によって管理されており、ユーザーの学習状態に合わせて最適な問題を自動で選びます。これにより、効率的で個別化された学習体験を提供します。

### Regex and Vector Search
AI がユーザーの情報（例えば「何を練習したか」「間違いがあるか」など）を知る必要がある時、普通の正規表現（regex）検索だけでは十分ではありません。vector（ベクトル）検索を使うと、「food」と検索した時に「orange」や「apple」なども見つけられます。そのため、SQLAlchemy の一部のフィールドは、テキストデータを vector 化して同期しています。この vector 化には Qdrant を使い、embedding model（埋め込みモデル）は変更可能です。デフォルトでは OpenAI の `text-embedding-3` を使って vector 化を行っています。