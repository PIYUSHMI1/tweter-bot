"""
post_once.py — used by GitHub Actions
Posts one tweet per run (no scheduler needed, GitHub handles timing)
"""

import tweepy
import google.generativeai as genai
import random
import os
from datetime import datetime

# Keys are injected by GitHub Actions as environment variables
TWITTER_API_KEY        = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET     = os.environ["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN   = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET  = os.environ["TWITTER_ACCESS_SECRET"]
GEMINI_API_KEY         = os.environ["GEMINI_API_KEY"]

ACCOUNT_BIO = """
You are a sharp FX and crypto trader with years of experience.
Your style is confident, concise, and data-driven.
You focus on price action, key levels, and risk management.
You trade pairs like EUR/USD, GBP/USD, USD/JPY, XAU/USD, BTC/USD, ETH/USD.
"""

def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")

def generate_content():
    model = init_gemini()
    hour = datetime.utcnow().hour
    day = datetime.utcnow().day

    # Morning run (8am) = analysis, Afternoon run (2pm) = setup or crypto
    if hour < 12:
        prompt = f"""
{ACCOUNT_BIO}
Write a morning market outlook tweet for {datetime.utcnow().strftime('%A')}.
Cover 1-2 of: EUR/USD, GBP/USD, USD/JPY, BTC/USD, XAU/USD.
Include key levels, bias, and one macro note. Under 260 chars.
Add hashtags. Output only the tweet text.
"""
    elif day % 2 == 0:
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD", "BTC/USD", "ETH/USD"]
        pair = random.choice(pairs)
        prompt = f"""
{ACCOUNT_BIO}
Write a trade setup tweet for {pair} with LONG/SHORT direction, entry, SL, TP1/TP2, brief reason, hashtags.
Under 260 chars. Output only the tweet text.
"""
    else:
        prompt = f"""
{ACCOUNT_BIO}
Write a crypto market update tweet on BTC and/or ETH.
Include sentiment, key level, bullish/bearish bias. Under 260 chars.
Add hashtags. Output only the tweet text.
"""

    response = model.generate_content(prompt)
    return response.text.strip()

def post_tweet(content):
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET
    )
    response = client.create_tweet(text=content)
    print(f"✅ Posted: {response.data['id']}")

if __name__ == "__main__":
    content = generate_content()
    print(f"Tweet:\n{content}\n")
    post_tweet(content)