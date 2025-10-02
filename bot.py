import os
import requests
import random
from openai import OpenAI

# ---- 環境変数 ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
IFTTT_URL = os.getenv("IFTTT_URL")
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG")  # 例: yourid-22

client = OpenAI(api_key=OPENAI_API_KEY)

# ---- ランダムクエリ ----
QUERIES = [
    "PS5 新作 ゲーム",
    "Nintendo Switch 新作",
    "Steam セール",
    "eスポーツ トレンド",
    "RPG 新作 発売日",
    "FPS 人気 ランキング"
]

def get_game_search_results():
    query = random.choice(QUERIES)
    print(f"検索クエリ: {query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "num": 3}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [(it.get("title", ""), it.get("link", "")) for it in items[:3]], query

# ---- Amazonリンク生成（検索URL + アソシエイトタグ）----
def get_amazon_link(keyword):
    base_url = "https://www.amazon.co.jp/s"
    return f"{base_url}?k={requests.utils.quote(keyword)}&tag={AMAZON_ASSOCIATE_TAG}"

# ---- 140文字以内に収める ----
def truncate_140(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= 140 else (text[:139] + "…")

# ---- ツイート生成 ----
def generate_tweet(title, url, query):
    # 3回に1回はAmazon検索リンクを使う
    if random.randint(1, 3) == 1:
        url = get_amazon_link(query)
        print(f"💡 Amazonリンクを使用: {url}")

    prompt = f"""
以下の情報をもとに、X（旧Twitter）で拡散されやすい日本語ツイートを1つ作成してください。

タイトル: {title}
URL: {url}

条件:
- 140文字以内（必ず）
- ゲームユーザーが関心を持つ内容
- URLはそのまま残す
- 宣伝っぽさを出さず自然に
- 必ず「#ゲーム #新作ゲーム」というハッシュタグを含める
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.8,
    )
    text = resp.choices[0].message.content.strip()
    return truncate_140(text)

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
        raise RuntimeError("検索結果が取得できませんでした。GOOGLE_CSE_ID を確認してください。")

    title, url = random.choice(search_results)
    tweet = generate_tweet(title, url, query)
    print("投稿予定:", tweet)
    post_to_x_via_ifttt(tweet)
