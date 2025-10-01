import os
import requests
import random
from datetime import datetime, timezone
from openai import OpenAI

# 環境変数
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
IFTTT_URL = os.environ["IFTTT_URL"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ランダムテーマ（30項目以上）
THEMES = [
    "自己肯定感を高める言葉",
    "一歩踏み出す勇気を与える言葉",
    "在宅でできる副業や収入のアイデア",
    "心を軽くするメンタルケアの知恵",
    "引きこもり経験から得られる強み",
    "安心できる日常の工夫",
    "人とのつながり方（オンライン中心）",
    "外に出なくても楽しめる趣味",
    "小さな成功体験の積み重ね",
    "自分を責めずに休む大切さ",
    "ストレスを和らげる呼吸法やリラックス法",
    "引きこもりでもできる健康習慣（軽い運動など）",
    "孤独感を和らげる考え方",
    "引きこもりをポジティブに捉える視点",
    "お金をかけずに楽しめる工夫",
    "心が落ち込んだ時の立ち直り方",
    "引きこもりを活かした創作活動のすすめ",
    "無理せずできる勉強やスキルアップ",
    "一人暮らしでも心地よく過ごす工夫",
    "小さなご褒美で自分を大切にする方法",
    "AIや最新ツールを活用した便利な暮らし",
    "在宅でできるボランティアや社会参加",
    "オンラインで安心して話せる居場所",
    "「休むこと」を肯定するメッセージ",
    "失敗を気にしない生き方のヒント",
    "小さな挑戦の積み重ねが大きな成果になる話",
    "自分だけのペースを守る大切さ",
    "引きこもりから見える社会への気づき",
    "心に寄り添う名言やことば",
    "生活リズムを整える小さな工夫",
    "部屋を快適にするプチ模様替えの提案",
    "睡眠を整える習慣",
    "孤独感を減らすペットや植物の存在",
    "在宅での収入源の最新情報",
    "自分を癒すセルフケアの方法",
    "引きこもりのバズる一言",
]

SYSTEM_PROMPT = (
    "あなたは『引きこもりの人に寄り添い励ますインフルエンサー』です。\n"
    "毎日、引きこもりの人に向けて有益な情報・気づき・言葉をX（旧Twitter）向けに発信してください。\n"
    "日本語で140字以内、絵文字は0〜2個まで。誤情報・煽りは禁止。\n"
    "難しすぎず、優しく語りかける文体で。"
)

def generate_tweet() -> str:
    today = datetime.now().strftime("%Y年%m月%d日")
    theme = random.choice(THEMES)  # ランダムにテーマ選択
    user_prompt = (
        f"{today}に投稿する、引きこもりの人に有益な内容を考えてください。\n"
        f"テーマは『{theme}』です。\n"
        "X向けに140字以内、日本語で書いてください。"
    )
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=280,
        temperature=0.9,
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
    print("🧠 GPTがランダムテーマで引きこもり向けツイート生成中...")
    tweet = generate_tweet()
    print("🐦 投稿内容:", tweet)
    resp = post_to_ifttt(tweet)
    now = datetime.now(timezone.utc).isoformat()
    print(f"[{now}] ✅ IFTTT経由で投稿完了:", resp)

if __name__ == "__main__":
    main()
