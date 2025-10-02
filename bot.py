import os
import random
import requests
from openai import OpenAI

# APIキーの取得
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
IFTTT_URL = os.environ["IFTTT_URL"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ゲーム関連の検索されやすいキーワードリスト
keywords = [
    "原神 最強武器", 
    "APEX 初心者向け", 
    "モンハン 新武器",
    "GTA6 発売日",
    "ポケモン 新作",
    "FF7 リメイク攻略",
    "無課金 裏技",
    "効率 レベル上げ"
]

# ランダムに1つ選択
chosen = random.choice(keywords)

# AIにツイート文を生成させる
prompt = f"ゲーム好き向けに「{chosen}」を含めたツイートを140文字以内で考えて。URLを最後に追加する想定。"

tweet = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=100
).choices[0].message.content.strip()

# IFTTT経由で投稿
payload = {"value1": tweet}
res = requests.post(IFTTT_URL, json=payload)

print("投稿内容:", tweet)
print("IFTTTレスポンス:", res.status_code)
