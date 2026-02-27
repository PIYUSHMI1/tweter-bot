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
    """Initialize Gemini model with correct model name."""
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-pro which is widely available
    return genai.GenerativeModel("gemini-pro")

def generate_content():
    """Generate tweet content based on time of day."""
    model = init_gemini()
    hour = datetime.utcnow().hour
    day = datetime.utcnow().day
    
    # Get current day name
    current_day = datetime.utcnow().strftime('%A')

    # Morning run (8am) = analysis
    if hour < 12:
        prompt = f"""
{ACCOUNT_BIO}
Write a morning market outlook tweet for {current_day}.
Cover 1-2 of: EUR/USD, GBP/USD, USD/JPY, BTC/USD, XAU/USD.
Include key levels, bias (bullish/bearish/neutral), and one brief macro note.
Keep it under 260 characters. Be confident and professional.
Add relevant hashtags like #forex #trading #EURUSD #BTC.
Output only the tweet text, nothing else.
"""
    # Afternoon run: alternate between trade setup and crypto
    elif day % 2 == 0:
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD", "BTC/USD", "ETH/USD"]
        pair = random.choice(pairs)
        prompt = f"""
{ACCOUNT_BIO}
Write a trade setup tweet for {pair}.
Include: LONG or SHORT direction, entry zone, stop loss, take profit (1 or 2 targets), and brief reason.
Format with line breaks for clarity. Keep under 260 characters.
Add relevant hashtags like #forex #trading #{pair.replace('/', '')}.
Output only the tweet text, nothing else.
"""
    else:
        prompt = f"""
{ACCOUNT_BIO}
Write a crypto market update tweet on BTC and/or ETH.
Include: current market sentiment, a key level to watch, and short-term bias (bullish/bearish).
Keep it under 260 characters. Be sharp and opinionated.
Add hashtags like #bitcoin #ethereum #crypto #BTC #ETH.
Output only the tweet text, nothing else.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating content: {e}")
        # Fallback tweet if Gemini fails
        return f"Monitoring {random.choice(['EUR/USD', 'BTC/USD', 'XAU/USD'])} today. Key levels holding. Will update soon. #forex #trading"

def post_tweet(content):
    """Post tweet to Twitter."""
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        response = client.create_tweet(text=content)
        print(f"✅ Posted successfully! Tweet ID: {response.data['id']}")
        return response
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        raise e

if __name__ == "__main__":
    print(f"🤖 Running Twitter bot at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Generate and post tweet
    content = generate_content()
    print(f"\n📝 Generated tweet:\n{content}\n")
    print(f"📊 Tweet length: {len(content)} characters")
    
    # Post to Twitter
    post_tweet(content)
    print("✅ Bot execution complete!")
