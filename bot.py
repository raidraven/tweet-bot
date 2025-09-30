import os
import requests
import random
from datetime import datetime, timezone
from openai import OpenAI

# 環境変数からAPIキーとIFTTT URLを取得
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
IFTTT_URL = os.environ["IFTTT_URL"]  # 例: https://maker.ifttt.com/trigger/post_to_x/with/key/xxxx

client = OpenAI(api_key=OPENAI_API_KEY)

# 今日の日付を和風表記で取得
today = datetime.today()
date_str = today.strftime("%Y年%m月%d日")

# 投稿テーマ（ゲーム・アニメ）
TOPICS = [
    f"{date_str}以降に発売・配信される最新のコンピューターゲーム情報（新作、アップデート、イベント）を、信頼できる公式サイトまたは大手メディアから取得し、URL付きで140字以内に要約してください。",
    f"{date_str}以降に放送・配信される最新のアニメ情報（新作、話題、イベント）を、信頼できる公式サイトまたは大手メディアから取得し、URL付きで140字以内に要約してください。",
]

# botの性格と制約
SYSTEM = (
    "あなたは日本のゲーム・アニメ情報に詳しい引きこもりインフルエンサーです。\n"
    "Twitter投稿向けに、日本語で140字以内に要約してください。\n"
    "URLは公式サイトまたは信頼できるニュースメディアのものを添えてください。\n"
    "絵文字は0〜2個まで使用可能です。\n"
    "煽りや誤情報は禁止です。古い情報は除外してください。"
)

def generate_tweet():
    topic = random.choice(TOPICS)
    prompt = f"次のテーマで1つだけ出力：{topic}"
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=280,
        temperature=0.9,
    )
    text = res.choices[0].message.content.strip()
    text = " ".join(text.split())  # 改行や余分な空白を除去

    # 文字数ガード（超えたら切り詰め）
    if len(text) > 140:
        text = text[:137] + "…"

    # 万が一空ならフォールバック
    if not text:
        text = "今日も生きてるだけで100点。焦らずいこう。"
    return text

def post_to_ifttt(text: str):
    r = requests.post(IFTTT_URL, json={"value1": text}, timeout=15)
    r.raise_for_status()
    return r.text

def main():
    tweet = generate_tweet()
    print("Tweet:", tweet)
    resp = post_to_ifttt(tweet)
    now = datetime.now(timezone.utc).isoformat()
    print(f"[{now}] posted via IFTTT:", resp)

if __name__ == "__main__":
    main()
