"""
post_once.py — TESTING MODE (prints instead of posts)
"""

import google.generativeai as genai
import random
import os
from datetime import datetime

# Keys are injected by GitHub Actions as environment variables
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

ACCOUNT_BIO = """
You are a sharp FX and crypto trader with years of experience.
Your style is confident, concise, and data-driven.
You focus on price action, key levels, and risk management.
"""

def init_gemini():
    """Initialize Gemini model."""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-pro")

def generate_content():
    """Generate tweet content based on time of day."""
    model = init_gemini()
    hour = datetime.utcnow().hour
    day = datetime.utcnow().day
    
    current_day = datetime.utcnow().strftime('%A')

    if hour < 12:
        prompt = f"""
{ACCOUNT_BIO}
Write a morning market outlook tweet for {current_day}.
Cover 1-2 of: EUR/USD, GBP/USD, USD/JPY, BTC/USD, XAU/USD.
Include key levels and bias. Under 260 chars.
Add hashtags. Output only the tweet text.
"""
    elif day % 2 == 0:
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD", "BTC/USD"]
        pair = random.choice(pairs)
        prompt = f"""
{ACCOUNT_BIO}
Write a trade setup tweet for {pair} with direction, entry, SL, TP.
Under 260 chars. Add hashtags. Output only the tweet text.
"""
    else:
        prompt = f"""
{ACCOUNT_BIO}
Write a crypto market update on BTC/ETH.
Include sentiment and key level. Under 260 chars.
Add hashtags. Output only the tweet text.
"""

    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    print(f"🤖 Running Twitter bot (TEST MODE) at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Generate content
    content = generate_content()
    print(f"\n📝 Generated tweet:\n{content}\n")
    print(f"📊 Tweet length: {len(content)} characters")
    print("\n✅ TEST PASSED! (No tweet was actually posted)")
    print("💡 To post for real, you need Twitter API credits")
