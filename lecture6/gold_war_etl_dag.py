# =============================================================================
# gold_war_etl_dag.py
# Mid-Semester Assignment – Gold Price & War News ML Pipeline
#
# Pipeline flow:
#   fetch_gold_prices ──┐
#                       ├──> compute_sentiment_and_merge ──> train_model
#   fetch_war_news   ──┘
# =============================================================================

import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_DIR  = os.path.join(os.path.expanduser("~"), "Documents", "Data_pipeline", "data")
MODEL_DIR = os.path.join(DATA_DIR, "models")

GOLD_START_DATE = "2024-01-01"
GOLD_SYMBOL     = "GC=F"           # Gold futures on Yahoo Finance

NYT_RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
]

# Keywords used to filter war/conflict-related news articles
WAR_KEYWORDS = {
    "war", "conflict", "attack", "military", "invasion",
    "troops", "missile", "combat", "battle", "offensive",
    "ceasefire", "airstrike", "bombing", "casualties", "soldier",
}

# ML features used for training and prediction
FEATURE_COLUMNS = ["close", "sentiment_mean", "news_count"]

# Output file paths
GOLD_CSV     = os.path.join(DATA_DIR, "gold_prices.csv")
NEWS_CSV     = os.path.join(DATA_DIR, "war_news.csv")
TRAINING_CSV = os.path.join(DATA_DIR, "training_data.csv")
MODEL_PKL    = os.path.join(MODEL_DIR, "gold_model.pkl")


# ── Helper ─────────────────────────────────────────────────────────────────────
def ensure_directories():
    """Create data and model directories if they don't exist yet."""
    os.makedirs(DATA_DIR,  exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)


# =============================================================================
# TASK 1 – Fetch gold prices from Yahoo Finance
# =============================================================================
def fetch_gold_prices():
    """
    Download daily gold futures prices (GC=F) from 2024-01-01 to today.
    Saves result to gold_prices.csv.

    Columns saved: date, open, high, low, close
    """
    import yfinance as yf
    import pandas as pd

    ensure_directories()
    today = datetime.today().strftime("%Y-%m-%d")

    logging.info(f"Downloading gold prices from {GOLD_START_DATE} to {today} ...")

    try:
        df = yf.download(GOLD_SYMBOL, start=GOLD_START_DATE, end=today, auto_adjust=True)

        # yfinance returns an empty DataFrame if the symbol is wrong or dates are invalid
        if df.empty:
            raise ValueError(
                f"No data returned for symbol '{GOLD_SYMBOL}'. "
                "Check the symbol name and date range."
            )

        # Keep only the four price columns and rename to lowercase
        df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].rename(columns=str.lower)
        df.index.name = "date"

        # Convert the DatetimeIndex to plain date strings (YYYY-MM-DD)
        df.index = df.index.strftime("%Y-%m-%d")

        df.to_csv(GOLD_CSV)
        logging.info(f"✅ Saved {len(df)} rows to {GOLD_CSV}")

    except Exception as e:
        logging.error(f"❌ fetch_gold_prices failed: {e}")
        raise   # Re-raise so Airflow marks the task as FAILED


# =============================================================================
# TASK 2 – Fetch war-related news from NYT RSS feeds
# =============================================================================
def fetch_war_news():
    """
    Pull articles from NYT RSS feeds and keep only those that contain
    at least one war/conflict keyword in the title or summary.
    Saves result to war_news.csv.

    Columns saved: date, title, summary
    """
    import feedparser
    import pandas as pd

    ensure_directories()

    records = []

    for feed_url in NYT_RSS_FEEDS:
        logging.info(f"Fetching RSS feed: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)

            # feedparser doesn't raise exceptions – check bozo flag for parse errors
            if feed.bozo:
                logging.warning(
                    f"Feed '{feed_url}' may be malformed: {feed.bozo_exception}"
                )

            if not feed.entries:
                logging.warning(f"No entries found in feed: {feed_url}")
                continue

            for entry in feed.entries:
                title   = entry.get("title",   "")
                summary = entry.get("summary", "")
                combined_text = (title + " " + summary).lower()

                # Only keep articles that match at least one war keyword
                is_war_related = any(kw in combined_text for kw in WAR_KEYWORDS)
                if not is_war_related:
                    continue

                # Parse the publication date
                pub = entry.get("published_parsed")
                if pub:
                    date = datetime(*pub[:3]).strftime("%Y-%m-%d")
                else:
                    logging.warning(f"Missing date for article: '{title}' – skipping")
                    continue

                records.append({
                    "date":    date,
                    "title":   title,
                    "summary": summary,
                })

        except Exception as e:
            # Log the error but continue with the next feed
            logging.error(f"❌ Error fetching feed '{feed_url}': {e}")
            continue

    # If no articles were collected from any feed, stop the pipeline
    if not records:
        raise RuntimeError(
            "No war-related articles were collected. "
            "Check your internet connection and the NYT RSS URLs."
        )

    df = pd.DataFrame(records)
    df.to_csv(NEWS_CSV, index=False)
    logging.info(f"✅ Saved {len(df)} war-related articles to {NEWS_CSV}")


# =============================================================================
# TASK 3 – Compute sentiment scores and merge with gold prices
# =============================================================================
def compute_sentiment_and_merge():
    """
    1. Load gold_prices.csv and war_news.csv
    2. Run TextBlob sentiment analysis on each news title
    3. Aggregate sentiment by date (mean polarity + article count)
    4. Left-join with gold prices (days without news get sentiment = 0)
    5. Create the target column: 1 if next day's close > today's close, else 0
    6. Save result to training_data.csv
    """
    import pandas as pd
    from textblob import TextBlob

    # ── Load gold prices ───────────────────────────────────────────────
    if not os.path.exists(GOLD_CSV):
        raise FileNotFoundError(
            f"Gold prices file not found at '{GOLD_CSV}'. "
            "Make sure fetch_gold_prices ran successfully first."
        )

    gold = pd.read_csv(GOLD_CSV, index_col=0)
    gold.index.name = "date"
    gold = gold.reset_index()
    gold["date"] = pd.to_datetime(gold["date"])
    logging.info(f"Loaded {len(gold)} gold price rows")

    # ── Load war news ──────────────────────────────────────────────────
    if not os.path.exists(NEWS_CSV):
        raise FileNotFoundError(
            f"War news file not found at '{NEWS_CSV}'. "
            "Make sure fetch_war_news ran successfully first."
        )

    news = pd.read_csv(NEWS_CSV)
    news["date"] = pd.to_datetime(news["date"])
    logging.info(f"Loaded {len(news)} news articles")

    # ── Sentiment analysis ─────────────────────────────────────────────
    def safe_sentiment(text):
        """Return TextBlob polarity score; return 0.0 if the text is empty."""
        if not isinstance(text, str) or text.strip() == "":
            return 0.0
        return TextBlob(text).sentiment.polarity

    news["sentiment"] = news["title"].apply(safe_sentiment)

    # Aggregate: one row per date
    daily_sentiment = (
        news.groupby("date")
        .agg(
            sentiment_mean=("sentiment", "mean"),
            news_count=("sentiment", "count"),
        )
        .reset_index()
    )

    # ── Merge gold prices with sentiment ───────────────────────────────
    # Left join keeps all trading days; missing sentiment days get 0
    merged = gold.merge(daily_sentiment, on="date", how="left")
    merged["sentiment_mean"] = merged["sentiment_mean"].fillna(0.0)
    merged["news_count"]     = merged["news_count"].fillna(0).astype(int)

    # ── Create target column ───────────────────────────────────────────
    # target = 1  →  next day's close is HIGHER than today's  (price goes UP)
    # target = 0  →  next day's close is LOWER  than today's  (price goes DOWN)
    merged = merged.sort_values("date").reset_index(drop=True)
    merged["target"] = (merged["close"].shift(-1) > merged["close"]).astype("Int64")

    # Drop the last row because it has no next-day price to compare with
    merged = merged.dropna(subset=["target"])

    # Sanity check: make sure we have enough data to train on
    if len(merged) < 10:
        raise ValueError(
            f"Only {len(merged)} training rows after merging. "
            "The dataset is too small to train a reliable model."
        )

    merged.to_csv(TRAINING_CSV, index=False)
    logging.info(f"✅ Saved {len(merged)} training rows to {TRAINING_CSV}")


# =============================================================================
# TASK 4 – Train a Random Forest classifier and save the model
# =============================================================================
def train_model():
    """
    1. Load training_data.csv
    2. Split into train / test sets (no shuffling – respects time order)
    3. Train a Random Forest classifier
    4. Print accuracy and classification report
    5. Save the trained model to gold_model.pkl
    """
    import pandas as pd
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    # ── Load training data ─────────────────────────────────────────────
    if not os.path.exists(TRAINING_CSV):
        raise FileNotFoundError(
            f"Training data not found at '{TRAINING_CSV}'. "
            "Make sure compute_sentiment_and_merge ran successfully first."
        )

    df = pd.read_csv(TRAINING_CSV)
    logging.info(f"Loaded {len(df)} training rows")

    # Verify all required feature columns are present
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing columns in training data: {missing_cols}. "
            f"Expected columns: {FEATURE_COLUMNS}"
        )

    X = df[FEATURE_COLUMNS]
    y = df["target"]

    # ── Train / test split ─────────────────────────────────────────────
    # shuffle=False is IMPORTANT for time-series data.
    # Shuffling would leak future prices into the training set, giving fake accuracy.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        shuffle=False,      # keep chronological order
    )

    logging.info(f"Train size: {len(X_train)} rows | Test size: {len(X_test)} rows")

    # ── Train model ────────────────────────────────────────────────────
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,    # fixed seed for reproducibility
    )
    model.fit(X_train, y_train)

    # ── Evaluate model ─────────────────────────────────────────────────
    predictions = model.predict(X_test)
    accuracy    = accuracy_score(y_test, predictions)

    logging.info(f"✅ Model accuracy on test set: {accuracy:.4f}")
    logging.info("\n" + classification_report(
        y_test, predictions,
        target_names=["Down (0)", "Up (1)"]
    ))

    # Warn if accuracy is suspiciously low – the model may need better features
    if accuracy < 0.50:
        logging.warning(
            "⚠️  Accuracy below 50% – the model is performing worse than random chance. "
            "Consider adding more features (e.g. lagged prices, moving averages)."
        )

    # ── Save model ─────────────────────────────────────────────────────
    ensure_directories()
    joblib.dump(model, MODEL_PKL)
    logging.info(f"✅ Model saved to {MODEL_PKL}")


# =============================================================================
# DAG definition
# =============================================================================
default_args = {
    "owner":   "student",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,   # retry once automatically if a task fails
}

with DAG(
    dag_id="gold_war_etl",
    default_args=default_args,
    schedule="@weekly",         # runs every Sunday at midnight
    catchup=False,              # don't run missed past weeks
    description="Gold price + war news ML pipeline – Mid-Semester Assignment",
    tags=["ml", "etl", "gold", "news"],
) as dag:

    t1_fetch_gold = PythonOperator(
        task_id="fetch_gold_prices",
        python_callable=fetch_gold_prices,
    )

    t2_fetch_news = PythonOperator(
        task_id="fetch_war_news",
        python_callable=fetch_war_news,
    )

    t3_merge = PythonOperator(
        task_id="compute_sentiment_and_merge",
        python_callable=compute_sentiment_and_merge,
    )

    t4_train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    # Task dependency: t1 and t2 run in parallel, then t3, then t4
    [t1_fetch_gold, t2_fetch_news] >> t3_merge >> t4_train