import os
import requests
from datetime import datetime, timezone
from openai import OpenAI

# 環境変数からキー取得
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
IFTTT_URL = os.environ["IFTTT_URL"]

client = OpenAI(api_key=OPENAI_API_KEY)

# GPTに渡すシステムプロンプト
SYSTEM_PROMPT = (
    "あなたは『引きこもりの人に寄り添い、励ますインフルエンサー』です。\n"
    "毎日、引きこもりの人に向けて、有益な情報・気づき・言葉をX（旧Twitter）向けに発信してください。\n"
    "日本語で140文字以内、絵文字は0〜2個まで。煽りや誤情報は禁止。\n"
    "投稿は「共感・安心・情報提供・自己肯定感・在宅ワーク」などをテーマに。\n"
    "難しすぎず、優しく語りかける文体でお願いします。"
)

def generate_tweet() -> str:
    today = datetime.now().strftime("%Y年%m月%d日")
    user_prompt = f"引きこもりの人に有益な情報や言葉を考えてください。140字以内で。"
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=280,
        temperature=0.85,
    )
    tweet = res.choices[0].message.content.strip()
    tweet = " ".join(tweet.split())
    if len(tweet) > 140:
        tweet = tweet[:137] + "…"
    return tweet

def post_to_ifttt(text: str):
    r = requests.post(IFTTT_URL, json={"value1": text}, timeout=15)
    r.raise_for_status()
    return r.text

def main():
    print("🧠 GPTが引きこもり向けツイート生成中...")
    tweet = generate_tweet()
    print("🐦 投稿内容:", tweet)
    resp = post_to_ifttt(tweet)
    now = datetime.now(timezone.utc).isoformat()
    print(f"[{now}] ✅ IFTTT経由で投稿完了:", resp)

if __name__ == "__main__":
    main()
