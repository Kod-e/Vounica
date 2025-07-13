import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
qdrant_url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
client = QdrantClient(url=qdrant_url)

# Create collection
def setup_collection():
    if not client.collection_exists("user_texts"):
        client.create_collection(
            collection_name="user_texts",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

# Get embedding from OpenAI
def get_embedding(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding

# Insert sample text
def insert_text(user_id: str, text: str, doc_type: str = "story"):
    vector = get_embedding(text)
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={"user_id": user_id, "text": text, "type": doc_type}
    )
    client.upsert(collection_name="user_texts", points=[point])

# Search for similar text
def search_text(user_id: str, query: str, top_k: int = 5):
    vector = get_embedding(query)
    return client.search(
        collection_name="user_texts",
        query_vector=vector,
        limit=top_k,
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
    )

# 批量插入样本数据
def insert_sample_data():
    # 用户1的样本 - 餐厅和食物相关 (中文)
    user1_samples_cn = [
        "今天在新开的日式餐厅吃了一碗特别正宗的拉面，汤头非常浓郁。",
        "周末和朋友去了那家有名的火锅店，点了牛肉和虾滑，味道很赞。",
        "家附近新开了一家面包店，他们的牛角面包松软可口，值得推荐。",
        "昨天尝试了自制意大利面，加了自制的番茄酱，味道出乎意料的好。",
        "公司附近有一家很隐蔽的寿司店，师傅是日本人，鱼生新鲜度很高。",
        "在外地旅游时偶然发现一家本地特色餐厅，他们的烤鱼非常入味。",
        "午餐时在商场美食广场吃了份炒河粉，辣度刚好，很合我的口味。",
        "朋友推荐的那家甜品店名不虚传，提拉米苏口感细腻，不会太甜。",
        "第一次尝试韩国部队锅，辛辣程度适中，里面的泡菜很开胃。",
        "在家用空气炸锅做了炸鸡翅，外酥里嫩，比外卖健康多了。"
    ]
    
    # 用户1的样本 - 餐厅和食物相关 (英文)
    user1_samples_en = [
        "Today I tried an authentic ramen at a newly opened Japanese restaurant, the broth was incredibly rich.",
        "Went to that famous hotpot place with friends over the weekend, ordered beef and shrimp balls, delicious.",
        "A new bakery opened near my home, their croissants are soft and delicious, highly recommended.",
        "Yesterday I made homemade pasta with my own tomato sauce, it turned out surprisingly good.",
        "There's a hidden sushi restaurant near my office with a Japanese chef, the sashimi is super fresh.",
        "While traveling I discovered a local specialty restaurant, their grilled fish was perfectly seasoned.",
        "Had some stir-fried noodles at the food court for lunch, the spice level was just right for me.",
        "The dessert shop my friend recommended lived up to the hype, the tiramisu was smooth and not too sweet.",
        "Tried Korean army stew for the first time, moderately spicy with kimchi that stimulates the appetite.",
        "Made chicken wings in my air fryer at home, crispy outside and tender inside, much healthier than takeout."
    ]
    
    # 用户1的样本 - 餐厅和食物相关 (日语)
    user1_samples_ja = [
        "今日、新しくオープンした日本食レストランで本格的なラーメンを食べました。スープがとても濃厚でした。",
        "週末に友達と有名な火鍋店に行き、牛肉とエビのつみれを注文しました。とても美味しかったです。",
        "家の近くに新しいパン屋がオープンしました。彼らのクロワッサンはふわふわで美味しく、お勧めです。",
        "昨日、自家製パスタと自家製トマトソースを作りました。予想以上に美味しかったです。",
        "オフィスの近くに隠れた寿司屋があり、シェフは日本人です。刺身が非常に新鮮です。",
        "旅行中に地元の特色あるレストランを見つけました。彼らの焼き魚は完璧に味付けされていました。",
        "ランチにフードコートで炒め麺を食べました。辛さのレベルが私にちょうど良かったです。",
        "友達がお勧めしたデザート店は評判通りでした。ティラミスはなめらかで甘すぎませんでした。",
        "初めて韓国のプデチゲを試しました。適度に辛く、キムチが食欲をそそります。",
        "家でエアフライヤーを使って鶏の手羽先を作りました。外はカリカリで中はジューシー、テイクアウトより健康的です。"
    ]
    
    # 用户2的样本 - 旅行相关 (中文)
    user2_samples_cn = [
        "上个月去了趟北海道，札幌的雪景美不胜收，还体验了温泉。",
        "去年夏天在海南三亚度假，沙滩洁白细腻，海水清澈见底。",
        "周末开车去郊外的山区徒步，登顶后俯瞰整个城市的感觉真好。",
        "去欧洲自助游最喜欢的城市是布拉格，古老的建筑和石板路很有韵味。",
        "春节期间去了云南大理，古城的历史氛围和洱海的美景让人难忘。",
        "背包客旅行体验了西藏拉萨，布达拉宫的壮观超出我的想象。",
        "在泰国清迈骑大象、逛夜市，体验了不同于国内的异域风情。",
        "自驾新疆独库公路，沿途的风景从荒漠到草原再到雪山，变化多端。",
        "乘坐火车穿越加拿大落基山脉，窗外的自然风光令人窒息。",
        "在京都的岚山竹林漫步，仿佛置身于电影场景中，非常治愈。"
    ]
    
    # 用户2的样本 - 旅行相关 (英文)
    user2_samples_en = [
        "Last month I went to Hokkaido, the snow scenery in Sapporo was breathtaking and I also experienced hot springs.",
        "Vacationed in Sanya, Hainan last summer, the beach was white and fine, the sea water clear to the bottom.",
        "Drove to the mountains in the suburbs for hiking on the weekend, the feeling of overlooking the entire city after reaching the top was great.",
        "Visited Dali, Yunnan during Spring Festival, the historical atmosphere of the ancient city and the beautiful scenery of Erhai Lake were unforgettable.",
        "Experienced backpacking in Lhasa, Tibet, the magnificence of Potala Palace exceeded my imagination.",
        "My favorite city during my European self-guided tour was Prague, the ancient buildings and cobblestone roads have great charm.",
        "Rode elephants and explored night markets in Chiang Mai, Thailand, experiencing exotic customs different from domestic ones.",
        "Self-drove on the Duku Highway in Xinjiang, the scenery along the way changed from desert to grassland to snow mountains, quite varied.",
        "Took a train through the Canadian Rockies, the natural scenery outside the window was breathtaking.",
        "Strolled through the bamboo forest in Arashiyama, Kyoto, felt like being in a movie scene, very healing."
    ]
    
    # 用户2的样本 - 旅行相关 (日语)
    user2_samples_ja = [
        "先月、北海道に行きました。札幌の雪景色は息をのむほど美しく、温泉も体験しました。",
        "去年の夏、海南島の三亜でバカンスを過ごしました。ビーチは白くきめ細かく、海水は底まで透き通っていました。",
        "週末に郊外の山にドライブしてハイキングに行きました。頂上から街全体を見下ろす感覚は素晴らしかったです。",
        "春節に雲南省の大理を訪れました。古城の歴史的な雰囲気と洱海の美しい景色は忘れられません。",
        "チベットのラサをバックパッカーとして体験しました。ポタラ宮の壮大さは私の想像を超えていました。",
        "ヨーロッパ自由旅行で一番好きな都市はプラハでした。古い建物と石畳の道には味わいがあります。",
        "タイのチェンマイで象に乗ったり、ナイトマーケットを散策したり、国内とは異なるエキゾチックな風習を体験しました。",
        "新疆のドゥクハイウェイをセルフドライブしました。砂漠から草原、雪山まで、道中の景色は多様に変化しました。",
        "カナディアンロッキーを列車で横断しました。窓の外の自然の景色は息をのむほどでした。",
        "京都の嵐山の竹林を散歩しました。映画のシーンにいるような感覚で、とても癒されました。"
    ]
    
    # 用户3的样本 - 技术和工作相关 (中文)
    user3_samples_cn = [
        "最近在学习Python的机器学习库，TensorFlow和PyTorch各有特色。",
        "公司项目从传统架构迁移到微服务，挑战不少但很有成就感。",
        "周末参加了一个区块链技术研讨会，对智能合约有了更深入的理解。",
        "在家办公期间优化了工作环境，新键盘和显示器大大提高了效率。",
        "团队开始使用敏捷开发方法，每日站会和冲刺规划让项目进度更透明。",
        "研究了几种NoSQL数据库，MongoDB对非结构化数据的处理很有优势。",
        "花了一周时间重构了代码库中的遗留系统，现在运行效率提高了30%。",
        "尝试了新的前端框架Vue.js，组件化的设计理念很适合我们的项目。",
        "公司引入了持续集成工具，自动化测试和部署大大减少了人为错误。",
        "在技术博客上分享了关于分布式系统的心得，收到了很多有价值的反馈。"
    ]
    
    # 用户3的样本 - 技术和工作相关 (英文)
    user3_samples_en = [
        "Recently learning Python's machine learning libraries, TensorFlow and PyTorch each have their own characteristics.",
        "Migrating company projects from traditional architecture to microservices, challenging but rewarding.",
        "Attended a blockchain technology seminar over the weekend, gained deeper understanding of smart contracts.",
        "Optimized my work environment during the work-from-home period, new keyboard and monitor greatly improved efficiency.",
        "The team started using agile development methods, daily stand-ups and sprint planning make project progress more transparent.",
        "Researched several NoSQL databases, MongoDB has advantages in processing unstructured data.",
        "Spent a week refactoring legacy systems in the codebase, now running efficiency has improved by 30%.",
        "Tried the new front-end framework Vue.js, the componentized design concept suits our project well.",
        "The company introduced continuous integration tools, automated testing and deployment greatly reduced human error.",
        "Shared insights about distributed systems on a tech blog, received a lot of valuable feedback."
    ]
    
    # 用户3的样本 - 技术和工作相关 (日语)
    user3_samples_ja = [
        "最近、PythonのTensorFlowやPyTorchなどの機械学習ライブラリを学んでいます。それぞれ特徴があります。",
        "会社のプロジェクトを従来のアーキテクチャからマイクロサービスに移行しています。課題は多いですが、やりがいがあります。",
        "週末にブロックチェーン技術のセミナーに参加し、スマートコントラクトについてより深く理解できました。",
        "在宅勤務期間に作業環境を最適化しました。新しいキーボードとモニターで効率が大幅に向上しました。",
        "チームはアジャイル開発手法の使用を開始しました。デイリースタンドアップとスプリント計画によりプロジェクトの進捗がより透明になりました。",
        "いくつかのNoSQLデータベースを研究しました。MongoDBは非構造化データの処理に利点があります。",
        "コードベースの古いシステムのリファクタリングに一週間かけました。現在、実行効率が30%向上しています。",
        "新しいフロントエンドフレームワークVue.jsを試しました。コンポーネント化された設計コンセプトは私たちのプロジェクトに適しています。",
        "会社は継続的インテグレーションツールを導入しました。自動テストとデプロイにより、人的ミスが大幅に減少しました。",
        "テックブログで分散システムに関する見識を共有し、多くの価値あるフィードバックを受け取りました。"
    ]
    
    # 将样本插入到数据库
    # 用户1 - 食物相关
    for text in user1_samples_cn:
        insert_text("user_1", text, "food_cn")
    for text in user1_samples_en:
        insert_text("user_1", text, "food_en")
    for text in user1_samples_ja:
        insert_text("user_1", text, "food_ja")
    
    # 用户2 - 旅行相关
    for text in user2_samples_cn:
        insert_text("user_2", text, "travel_cn")
    for text in user2_samples_en:
        insert_text("user_2", text, "travel_en")
    for text in user2_samples_ja:
        insert_text("user_2", text, "travel_ja")
    
    # 用户3 - 技术相关
    for text in user3_samples_cn:
        insert_text("user_3", text, "tech_cn")
    for text in user3_samples_en:
        insert_text("user_3", text, "tech_en")
    for text in user3_samples_ja:
        insert_text("user_3", text, "tech_ja")

# 测试搜索功能
def test_search():
    # 用户1的食物相关查询 - 多语言
    food_queries = {
        "中文": ["拉面", "日本料理", "面包", "自制美食", "火锅"],
        "English": ["ramen", "Japanese food", "bakery", "homemade", "hotpot"],
        "日本語": ["ラーメン", "日本食", "パン屋", "自家製", "火鍋"]
    }
    
    # 用户2的旅行相关查询 - 多语言
    travel_queries = {
        "中文": ["北海道", "海滩度假", "徒步旅行", "古城", "自然风光"],
        "English": ["Hokkaido", "beach vacation", "hiking", "ancient city", "natural scenery"],
        "日本語": ["北海道", "ビーチバカンス", "ハイキング", "古都", "自然景観"]
    }
    
    # 用户3的技术相关查询 - 多语言
    tech_queries = {
        "中文": ["Python", "微服务", "数据库", "前端开发", "自动化测试"],
        "English": ["Python", "microservices", "database", "front-end", "automated testing"],
        "日本語": ["Python", "マイクロサービス", "データベース", "フロントエンド", "自動テスト"]
    }
    
    # 测试用户1的多语言食物查询
    print("\n===== 用户1的食物相关搜索结果 =====")
    for lang, queries in food_queries.items():
        print(f"\n----- {lang}查询 -----")
        for query in queries:
            print(f"\n>> 查询: '{query}'")
            results = search_text("user_1", query)
            if results:
                for i, r in enumerate(results, 1):
                    if r and r.payload and "text" in r.payload:
                        print(f"{i}. 相似度: {r.score:.4f} - {r.payload['text']}")
    
    # 测试用户2的多语言旅行查询
    print("\n===== 用户2的旅行相关搜索结果 =====")
    for lang, queries in travel_queries.items():
        print(f"\n----- {lang}查询 -----")
        for query in queries:
            print(f"\n>> 查询: '{query}'")
            results = search_text("user_2", query)
            if results:
                for i, r in enumerate(results, 1):
                    if r and r.payload and "text" in r.payload:
                        print(f"{i}. 相似度: {r.score:.4f} - {r.payload['text']}")
    
    # 测试用户3的多语言技术查询
    print("\n===== 用户3的技术相关搜索结果 =====")
    for lang, queries in tech_queries.items():
        print(f"\n----- {lang}查询 -----")
        for query in queries:
            print(f"\n>> 查询: '{query}'")
            results = search_text("user_3", query)
            if results:
                for i, r in enumerate(results, 1):
                    if r and r.payload and "text" in r.payload:
                        print(f"{i}. 相似度: {r.score:.4f} - {r.payload['text']}")

# Example usage
if __name__ == "__main__":
    setup_collection()
    print("初始化示例数据...")
    insert_sample_data()
    print("数据插入完成，开始搜索测试...")
    test_search()