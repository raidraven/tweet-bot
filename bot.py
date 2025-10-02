import os
import requests
import random
from openai import OpenAI

# ---- 環境変数 ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
IFTTT_URL = os.getenv("IFTTT_URL")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---- 人気商品（アソシエイトリンク付き）----
AMAZON_PRODUCTS = [
    # 本体
    ("PS5本体", f"https://amzn.to/486hu7D?tag={AMAZON_ASSOCIATE_TAG}"),  # PS5本体
    ("Switch 有機ELモデル", f"https://amzn.to/3IKQobU?tag={AMAZON_ASSOCIATE_TAG}"),  # Switch OLED
    ("Steam Deck", f"https://amzn.to/3ITuvXV?tag={AMAZON_ASSOCIATE_TAG}"), # Steam Deck
    ("Meta Quest 3", f"https://amzn.to/48LYZWj?tag={AMAZON_ASSOCIATE_TAG}"), # Meta Quest 3

    # 新作・人気ソフト
    ("FF7リバース", f"https://amzn.to/486iCYV?tag={AMAZON_ASSOCIATE_TAG}"),  # FF7リバース
    ("モンハン ワイルズ", f"https://amzn.to/46vM9Ko?tag={AMAZON_ASSOCIATE_TAG}"),   # モンハン ワイルズ
    ("スプラトゥーン3", f"https://amzn.to/3IFKUiE?tag={AMAZON_ASSOCIATE_TAG}"),  # スプラトゥーン3
    ("ゼルダの伝説ティアーズオブキングダム", f"https://amzn.to/4pRZ0Os?tag={AMAZON_ASSOCIATE_TAG}"),  # ゼルダ 

    # 周辺機器
    ("Logicool G マウス", f"https://amzn.to/4o51cAO?tag={AMAZON_ASSOCIATE_TAG}"),  # Logicool G マウス
    ("Razer BlackShark V2", f"https://amzn.to/4nHgNXh?tag={AMAZON_ASSOCIATE_TAG}"), # Razer BlackShark V2
    ("DualSense Edge", f"https://amzn.to/42lpVs7?tag={AMAZON_ASSOCIATE_TAG}"), # DualSense Edge
]

# ---- ランダムクエリ（Google検索用）----
QUERIES = [
    "新作PS5ゲーム",
    "新作Switchゲーム",
    "新作スマホゲーム",
    "Steam セール",
    "コンピューターゲームイベント情報",
    "話題のコンピューターゲームニュース"
]

def get_game_search_results():
    query = random.choice(QUERIES)
    print(f"検索クエリ: {query}")
    print("GOOGLE_API_KEY:", GOOGLE_API_KEY)
    print("GOOGLE_CSE_ID:", GOOGLE_CSE_ID)
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "num": 10, "sort": "date"}
    r = requests.get(url, params=params, timeout=20)
    print("リクエストURL:", r.url)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [(it.get("title", ""), it.get("link", "")) for it in items], query

def get_amazon_product_link():
    return random.choice(AMAZON_PRODUCTS)

# ---- ツイート生成 ----
def truncate_140(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= 140 else (text[:139] + "…")

def generate_tweet(title, url, query):
    use_amazon = (random.randint(1, 3) == 1) # 3回に1回はAmazon人気商品リンクを使用
    if use_amazon:
        title, url = get_amazon_product_link()
        print(f"💡 Amazon人気商品リンクを使用: {title} {url}")

    styles = [
        "共感型（あるあるネタや日常体験）",
        "速報型（最新ニュースっぽく）",
        "問いかけ型（ユーザーに意見を求める）",
        "ユーモア型（大喜利やジョークを交える）"
    ]
    style = random.choice(styles)

    if use_amazon:
        prompt = f"""
                    以下の商品をPRするツイートを作成してください。

                    商品名: {title}
                    URL: {url}

                    条件:
                    - 140文字以内
                    - 誘導的な言葉（今すぐ / 注目 / 必見 など）を入れる
                    - ハッシュタグ: #ゲーム #新作ゲーム
                    - URLは必ず完全な形で残す
                    - 絵文字も交えて拡散されやすく
                    """
    else:
        prompt = f"""
            以下の情報をもとに、X（旧Twitter）で拡散されやすい日本語ツイートを1つ作成してください。

            タイトル: {title}
            URL: {url}

            条件:
            - 140文字以内
            - ゲーム好きが「いいね」「リツイート」したくなる内容
            - 宣伝っぽさはNG、フォロワー増加を優先
            - 必ず「#ゲーム #新作ゲーム」を含める
            - 文体: {style}
            - URLは必ず完全な形で残す
            - 絵文字の種類や語尾は毎回変える
            """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=140,
        temperature=1.0,
    )
    return truncate_140(resp.choices[0].message.content.strip())

# ---- IFTTT経由で投稿 ----
def post_to_x_via_ifttt(tweet):
    payload = {"value1": tweet}
    r = requests.post(IFTTT_URL, json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"IFTTTエラー: {r.status_code} {r.text}")
    print("✅ IFTTT送信成功:", tweet)

# ---- メイン処理 ----
if __name__ == "__main__":
    search_results, query = get_game_search_results()
    if not search_results:
        raise RuntimeError("検索結果が取得できませんでした。")
    
    title, url = random.choice(search_results)
    tweet = generate_tweet(title, url, query)
    print("投稿予定:", tweet)
    post_to_x_via_ifttt(tweet)



