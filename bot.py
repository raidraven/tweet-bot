import os
import requests
import random
from openai import OpenAI

# ---- 環境変数 ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
IFTTT_URL = os.getenv("IFTTT_URL")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---- 1) ランダムクエリ ----
QUERIES = [
    "PS5 新作 ゲーム",
    "Nintendo Switch 新作",
    "Steam 最新 セール",
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
    return [(it.get("title", ""), it.get("link", "")) for it in items[:3]]

# ---- 2) ツイート生成（ハッシュタグを必ず入れる）----
def truncate_140(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= 140 else (text[:139] + "…")

def generate_tweet(title, url):
    prompt = f"""
以下の検索結果のタイトルをもとに、X（旧Twitter）で拡散されやすい日本語ツイートを1つ作成してください。

検索結果タイトル: {title}
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

# ---- 3) IFTTT経由で投稿 ----
def post_to_x_via_ifttt(tweet):
    payload = {"value1": tweet}
    r = requests.post(IFTTT_URL, json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"IFTTTエラー: {r.status_code} {r.text}")
    print("✅ IFTTT送信成功:", tweet)

# ---- メイン処理 ----
if __name__ == "__main__":
    search_results = get_game_search_results()
    if not search_results:
        raise RuntimeError("検索結果が取得できませんでした。GOOGLE_CSE_ID を確認してください。")

    title, url = random.choice(search_results)  # 3件のうちランダムに選択
    tweet = generate_tweet(title, url)
    print("投稿予定:", tweet)
    post_to_x_via_ifttt(tweet)
