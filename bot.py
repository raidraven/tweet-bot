import os
import requests
import openai

# 環境変数
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
IFTTT_URL = os.getenv("IFTTT_URL")  # 例: https://maker.ifttt.com/trigger/tweet/with/key/xxxx

openai.api_key = OPENAI_API_KEY

# 1. ニュース取得
def get_trending_news(query="ゲーム アニメ AI 最新ニュース"):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    r = requests.get(url).json()
    if "items" in r:
        return [(item["title"], item["link"]) for item in r["items"][:3]]
    return []

# 2. ツイート生成
def generate_tweet(title, url):
    prompt = f"""
    以下のニュースを元に、X（旧Twitter）で拡散されやすいツイートを作ってください。

    ニュース: {title}
    URL: {url}

    条件:
    - 140文字以内
    - ゲーム/アニメ/AIユーザー向け
    - 絵文字やハッシュタグを活用
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.8,
    )
    return response["choices"][0]["message"]["content"].strip()

# 3. IFTTT経由で投稿
def post_to_x_via_ifttt(tweet):
    payload = {"value1": tweet}
    r = requests.post(IFTTT_URL, json=payload)
    print("IFTTTに送信:", tweet, "ステータス:", r.status_code)

# メイン処理
if __name__ == "__main__":
    news_list = get_trending_news()
    for title, url in news_list:
        tweet = generate_tweet(title, url)
        print("投稿予定:", tweet)
        post_to_x_via_ifttt(tweet)
