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