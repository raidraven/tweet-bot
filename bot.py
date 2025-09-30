import os, requests, random, textwrap
from datetime import datetime, timezone
from openai import OpenAI
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
IFTTT_URL = os.environ["IFTTT_URL"]  # 例: https://maker.ifttt.com/trigger/post_to_x/with/key/xxxx

client = OpenAI(api_key=OPENAI_API_KEY)

today = datetime.today()
date_str = today.strftime("%Y年%m月%d日")  # 和風表記にもできる

# お好みでテーマを増やせます
TOPICS = [
    f"「今日以降に発売予定のコンピューターゲームの新作情報に加えて、最新のアップデート、話題のトレンド、注目のイベント情報も含めて紹介してください。情報は{date_str}以降のものに限定し、過去のタイトルや古いニュースは除外してください。各項目には、公式サイトまたは信頼できるニュースメディアへのURLを添えてください。」",
    f"「今日以降に放送・配信予定の新作アニメに加えて、最新話題、注目のイベント、トレンド情報も含めて紹介してください。情報は{date_str}以降のものに限定し、過去の作品や古いニュースは除外してください。各項目には、公式サイトまたは信頼できるニュースメディアへのURLを添えてください。」",
]

SYSTEM = (
    "あなたは引きこもりインフルエンサー"
    "日本語でURLも含めて140字以内で要約して下さい"
    "絵文字は0〜2個まで、煽りや誤情報はNG。"
    "サイバーパンク風の語り口で"
)

def generate_tweet():
    topic = random.choice(TOPICS)
    prompt = f"次のテーマで1つだけ出力：{topic}。改行や前後の解説は不要。"
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.9,
    )
    text = res.choices[0].message.content.strip()

    # 文字数ガード（超えたら切り詰め）
    text = " ".join(text.split())
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
















