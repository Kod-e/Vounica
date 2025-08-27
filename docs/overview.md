ソフトの後端レイヤー
私は Core → Infra → Service → API という形で作りました。こうすると、ソフトの管
理や整理がしやすいです。
コードは全部 async で書きました。
Core は基本の部分です。たとえば db session を作る方法、Qdrant client、JWT の作
成などです。アプリをスタートするときに必要な初期化もここにjあります。
Coreの詳細コードは app/core を見てください
Infra は db model の定義です。uow (Unit of Work) を外に出すのもここです。schema
の定義や、vector db collection の定義もあります。そして repo を使って db の操作を
まとめます。もしあるフィールドが semantic search を必要とするときは、vector db
にも同じデータを入れます。
Infraの詳細コードはapp/infra を見てください
UoW(Unit of Work) は Infra の中で一番大事です。FastAPI の request ごとに、1つの
db session と user info をまとめて提供します。
uow は request で自動的に入って、ContextVar に保存されます。これで request の中
ならどこからでも user id、残り token quota、db session が取れます。request が終わっ
たら 、aclose を通して uow の処理が実行されます。
6
Uowの詳細コードは app/core を見てください
Qdrant は transaction がありません。だから保存したらすぐ反映されます。でも ORM
には transaction があって、error のとき rollback できます。この差で db と Qdrant の
データがずれる可能性があります。
そのため私は uow に「仮の transaction」を作りました。Qdrant の操作を一時的にた
めて、request が成功したら commit、失敗したら消すようにしました。これで同期の
問題を防ぎました。
Service レイヤーは実際の機能です。ここは量が多いので次で説明します。
Serviceの詳細コードはapp/service を見てください
API レイヤーは Infra の schema を使って Service の機能を呼び出します。
APIの詳細コードはapp/api/v1/endpoints を見てください