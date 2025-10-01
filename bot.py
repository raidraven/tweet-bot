import os
import requests
from datetime import datetime, timezone
from openai import OpenAI

# 環境変数からキーを取得
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CSE_ID = os.environ["GOOGLE_CSE_ID"]
IFTTT_URL = os.environ["IFTTT_URL"]

client = OpenAI(api_key=OPENAI_API_KEY)

# 今日の日付（和風表記）
today = datetime.today()
date_str = today.strftime("%Y年%m月%d日")

# 検索クエリ（ゲーム・アニメ）
SEARCH_QUERIES = [
    f"{date_str}以降のゲームイベント情報",
    f"{date_str}以降のゲーム発売日情報",
    f"{date_str}以降のゲームアップデート情報",
]

# GPT用プロンプト
SYSTEM_PROMPT = (
    "あなたは日本のゲーム・アニメ情報に詳しい引きこもりインフルエンサーです。\n"
    "Twitter投稿向けに、日本語で140字以内に要約してください。\n"
    "URLはツイートに関連したものを載せてください\n"
    "絵文字は0〜2個まで使用可能です。\n"
    "煽りや誤情報は禁止です。古い情報は除外してください。"
)

def google_search(query: str) -> str:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 5,
        "hl": "ja"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    results = r.json()
    texts = []
    for item in results.get("items", []):
        title = item.get("title")
        snippet = item.get("snippet")
        link = item.get("link")
        texts.append(f"{title}：{snippet}（{link}）")
    return "\n".join(texts)

def summarize_with_gpt(text: str) -> str:
    prompt = f"以下の検索結果をもとに、Twitter向けに140字以内で要約してください：\n{text}"
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=280,
        temperature=0.7,
    )
    summary = res.choices[0].message.content.strip()
    summary = " ".join(summary.split())
    if len(summary) > 140:
        summary = summary[:137] + "…"
    if not summary:
        summary = "今日も生きてるだけで100点。焦らずいこう。"
    return summary

def post_to_ifttt(text: str):
    r = requests.post(IFTTT_URL, json={"value1": text}, timeout=15)
    r.raise_for_status()
    return r.text

def main():
    query = SEARCH_QUERIES[datetime.today().day % len(SEARCH_QUERIES)]
    print("🔍 Google検索:", query)
    search_result = google_search(query)
    print("🧠 GPT要約中...")
    tweet = summarize_with_gpt(search_result)
    print("🐦 投稿内容:", tweet)
    resp = post_to_ifttt(tweet)
    now = datetime.now(timezone.utc).isoformat()
    print(f"[{now}] ✅ IFTTT経由で投稿完了:", resp)

if __name__ == "__main__":
    main()



