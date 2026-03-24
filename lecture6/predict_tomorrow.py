# predict_tomorrow.py

import joblib
import yfinance as yf
import feedparser
import pandas as pd
from textblob import TextBlob
from datetime import datetime

# ── Load the trained model ─────────────────────────────────────────────────
import os
model = joblib.load(os.path.expanduser("~/data/models/gold_model.pkl"))

# ── Get TODAY's gold closing price ─────────────────────────────────────────
today = datetime.today().strftime("%Y-%m-%d")
df = yf.download("GC=F", period="1d", auto_adjust=True)
df.columns = df.columns.get_level_values(0)
todays_close = float(df["Close"].iloc[-1])
print(f"Today's gold close: ${todays_close:.2f}")

# ── Get TODAY's war news sentiment ─────────────────────────────────────────
WAR_KEYWORDS = {
    "war", "conflict", "attack", "military", "invasion",
    "troops", "missile", "combat", "battle", "offensive",
}

NYT_RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
]

scores = []
for url in NYT_RSS_FEEDS:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
        if any(kw in text for kw in WAR_KEYWORDS):
            score = TextBlob(entry.get("title", "")).sentiment.polarity
            scores.append(score)

sentiment_mean = sum(scores) / len(scores) if scores else 0.0
news_count     = len(scores)
print(f"War news sentiment: {sentiment_mean:.3f}")
print(f"War news count:     {news_count}")

# ── Build today's feature row ──────────────────────────────────────────────
features = pd.DataFrame([{
    "close":          todays_close,
    "sentiment_mean": sentiment_mean,
    "news_count":     news_count,
}])

# ── Predict ────────────────────────────────────────────────────────────────
prediction   = model.predict(features)[0]
probability  = model.predict_proba(features)[0]
print()
print("=" * 40)
print("   TOMORROW'S GOLD PREDICTION")
print("=" * 40)
if prediction == 1:
    print(f"  Direction : ⬆️  UP")
else:
    print(f"  Direction : ⬇️  DOWN")
print(f"  Confidence: {max(probability) * 100:.1f}%")
print("=" * 40)