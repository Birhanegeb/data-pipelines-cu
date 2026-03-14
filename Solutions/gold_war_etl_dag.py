"""
Lecture 6 - Mid-Semester Assignment: Gold Price & War News ML Pipeline

ETL DAG that:
1. Fetches gold prices from 2024 to today (yfinance / any gold API)
2. Fetches war-related news from NYT RSS (https://www.nytimes.com/rss)
3. Computes sentiment on war news
4. Trains ML model to predict gold price up/down from sentiment
5. Saves model and data for submission

Schedule: @weekly - deploys new model every week
"""

from datetime import datetime
from pathlib import Path

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.operators.python_operator import PythonOperator

# Output paths - adjust for your environment
DATA_DIR = Path("/data/gold_war_pipeline")
MODEL_DIR = DATA_DIR / "models"
GOLD_CSV = DATA_DIR / "gold_prices.csv"
NEWS_CSV = DATA_DIR / "war_news.csv"
TRAINING_CSV = DATA_DIR / "training_data.csv"
MODEL_PATH = MODEL_DIR / "gold_model.pkl"

# NYT RSS feeds - World feed contains war/conflict news
NYT_RSS_URLS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]
WAR_KEYWORDS = ["war", "conflict", "attack", "military", "invasion", "strike", "battle"]


def _fetch_gold_prices(**context):
    """Fetch gold prices from 2024-01-01 to today. Uses yfinance (GC=F)."""
    import pandas as pd

    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("pip install yfinance")

    start = "2024-01-01"
    end = datetime.now().strftime("%Y-%m-%d")
    gold = yf.download("GC=F", start=start, end=end, progress=False, auto_adjust=True)

    if gold.empty:
        raise ValueError("No gold price data returned. Check symbol (GC=F) or date range.")

    gold = gold.reset_index()
    # Handle MultiIndex columns (yfinance sometimes returns these)
    if hasattr(gold.columns, "levels"):
        gold.columns = [str(c).lower().replace(" ", "_") for c in gold.columns.get_level_values(0)]
    else:
        gold.columns = [str(c).lower().replace(" ", "_") for c in gold.columns]
    if "date" not in gold.columns and "datetime" in gold.columns:
        gold = gold.rename(columns={"datetime": "date"})
    gold["date"] = pd.to_datetime(gold["date"]).dt.strftime("%Y-%m-%d")

    GOLD_CSV.parent.mkdir(parents=True, exist_ok=True)
    gold.to_csv(GOLD_CSV, index=False)
    print(f"Saved {len(gold)} rows to {GOLD_CSV}")
    return str(GOLD_CSV)


def _fetch_war_news(**context):
    """Fetch war-related news from NYT RSS. Filter by keywords."""
    import csv
    from datetime import datetime

    try:
        import feedparser
        import requests
    except ImportError:
        raise ImportError("pip install feedparser requests")

    rows = []
    for url in NYT_RSS_URLS:
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as e:
            print(f"Warning: Could not fetch {url}: {e}")
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = (title + " " + summary).lower()
            if any(kw in text for kw in WAR_KEYWORDS):
                pub = entry.get("published_parsed")
                if pub:
                    date_str = datetime(*pub[:3]).strftime("%Y-%m-%d")
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                rows.append({
                    "date": date_str,
                    "title": title[:200],
                    "summary": summary[:500] if summary else "",
                })

    NEWS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(NEWS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "title", "summary"])
        w.writeheader()
        w.writerows(rows)

    print(f"Saved {len(rows)} war-related articles to {NEWS_CSV}")
    return str(NEWS_CSV)


def _compute_sentiment_and_merge(**context):
    """Compute sentiment on news, merge with gold prices, create target (up/down)."""
    import pandas as pd

    try:
        from textblob import TextBlob
    except ImportError:
        raise ImportError("pip install textblob")

    gold = pd.read_csv(GOLD_CSV)
    gold["date"] = pd.to_datetime(gold["date"])

    news = pd.read_csv(NEWS_CSV)
    news["date"] = pd.to_datetime(news["date"])

    def sentiment(text):
        if pd.isna(text) or str(text).strip() == "":
            return 0.0
        return TextBlob(str(text)).sentiment.polarity

    news["sentiment"] = (news["title"] + " " + news["summary"]).apply(sentiment)
    daily_sent = news.groupby("date")["sentiment"].agg(["mean", "count"]).reset_index()
    daily_sent.columns = ["date", "sentiment_mean", "news_count"]

    gold_sorted = gold.sort_values("date")
    gold_sorted["price_next"] = gold_sorted["close"].shift(-1)
    gold_sorted["target"] = (gold_sorted["price_next"] > gold_sorted["close"]).astype(int)
    gold_sorted = gold_sorted.dropna(subset=["target"])

    merged = gold_sorted.merge(daily_sent, on="date", how="left")
    merged["sentiment_mean"] = merged["sentiment_mean"].fillna(0)
    merged["news_count"] = merged["news_count"].fillna(0)

    TRAINING_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(TRAINING_CSV, index=False)
    print(f"Saved training data {len(merged)} rows to {TRAINING_CSV}")
    return str(TRAINING_CSV)


def _train_model(**context):
    """Train ML model: predict gold price up (1) or down (0) from sentiment."""
    import pickle

    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(TRAINING_CSV)
    features = ["close", "sentiment_mean", "news_count"]
    X = df[features].fillna(0)
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"Model accuracy on test set: {score:.3f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": features}, f)
    print(f"Saved model to {MODEL_PATH}")
    return str(MODEL_PATH)


dag = DAG(
    dag_id="lecture6_gold_war_ml_pipeline",
    start_date=airflow.utils.dates.days_ago(14),
    schedule="@weekly",  # Run weekly to deploy new model
    catchup=False,
    tags=["lecture6", "mid-semester", "gold", "ml", "etl"],
)

fetch_gold = PythonOperator(
    task_id="fetch_gold_prices",
    python_callable=_fetch_gold_prices,
    dag=dag,
)

fetch_news = PythonOperator(
    task_id="fetch_war_news",
    python_callable=_fetch_war_news,
    dag=dag,
)

merge_and_sentiment = PythonOperator(
    task_id="compute_sentiment_and_merge",
    python_callable=_compute_sentiment_and_merge,
    dag=dag,
)

train_model = PythonOperator(
    task_id="train_model",
    python_callable=_train_model,
    dag=dag,
)

[fetch_gold, fetch_news] >> merge_and_sentiment >> train_model
