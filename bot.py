import os
import requests
from openai import OpenAI

# ---- 環境変数から取得（GitHub Secretsに保存して使う）----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
IFTTT_URL = os.getenv("IFTTT_URL")  # https://maker.ifttt.com/trigger/post_to_x/with/key/xxxxx

client = OpenAI(api_key=OPENAI_API_KEY)

# ---- 1) ニュース取得 ----
def get_trending_news(query="ゲーム アニメ AI 最新ニュース"):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    items = r.json().get("items", [])[:3]
    return [(it.get("title", ""), it.get("link", "")) for it in items]

# ---- 2) ツイート生成（最新API形式）----
def truncate_140(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= 140 else (text[:139] + "…")

def generate_tweet(title, url):
    prompt = f"""
以下のニュースを元に、X（旧Twitter）で拡散されやすい日本語ツイートを1つ作成してください。

ニュース: {title}
URL: {url}

条件:
- 140文字以内
- ゲーム/アニメ/AIユーザー向け
- 絵文字やハッシュタグを適度に活用
- 宣伝っぽさを出さない
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",   # 最新 & 高速モデル
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
    news_list = get_trending_news()
    if not news_list:
        raise RuntimeError("ニュースが取得できませんでした。GOOGLE_CSE_ID の設定を確認してください。")

    # テストとして最初のニュース1件だけ投稿
    title, url = news_list[0]
    tweet = generate_tweet(title, url)
    print("投稿予定:", tweet)
    post_to_x_via_ifttt(tweet)
