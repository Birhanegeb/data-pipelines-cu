# Mid-Semester Assignment - Gold Price & War News ML Pipeline
### Datapipeline Engineering | March 24, 2026| @Birhane G.

---

## Gold API Used
**yfinance** — free, no API key required
Symbol: `GC=F` (COMEX gold futures), date range: `2024-01-01` to today

---

## Model Accuracy
**0.8804 (88%)** on 560 rows evaluated

---

## What Was Done — Step by Step

### Step 1: Fetch Gold Prices
- Used `yfinance` to download daily gold futures prices from January 1, 2024 to today
- Saved columns: `date`, `open`, `high`, `low`, `close`
- Result: **560 trading day rows** saved to `gold_prices.csv`

### Step 2: Fetch War-Related News
- Fetched two NYT RSS feeds: **World** and **HomePage**
- Filtered articles using war/conflict keywords: `war`, `conflict`, `attack`, `military`, `invasion`, `troops`, `missile`, `combat`, `battle`, `offensive`, `ceasefire`, `airstrike`, `bombing`, `casualties`, `soldier`
- Saved matching articles with `date`, `title`, `summary` to `war_news.csv`
- Steps 1 and 2 ran **in parallel** in the pipeline

### Step 3: Sentiment Analysis and Merge
- Applied **TextBlob polarity analysis** on each article title
- Polarity score ranges from -1.0 (negative) to +1.0 (positive)
- Aggregated scores per date: `sentiment_mean` and `news_count`
- Left-joined with gold prices — trading days with no news received `sentiment_mean=0`
- Created binary **target column**:
  - `1` → next day closing price is **higher** (price goes UP)
  - `0` → next day closing price is **lower** (price goes DOWN)
- Saved result to `training_data.csv`

### Step 4: Train and Save the Model
- Trained a **Random Forest classifier** on three features:
  - `close` — gold closing price
  - `sentiment_mean` — mean sentiment of war news that day
  - `news_count` — number of war articles published that day
- Used `shuffle=False` in the 80/20 train/test split to preserve chronological order and prevent data leakage
- Saved trained model to `gold_model.pkl`

---

## Test model

Run `test_model.py` from the terminal with the following command:

```bash
python tests/test_model.py \
  --model data/models/gold_model.pkl \
  --data  data
```

### Test Output

```
✅ Model loaded from: data/models/gold_model.pkl
✅ Data loaded: 560 rows from 'data/training_data.csv'

==================================================
         MODEL EVALUATION RESULTS
==================================================
  Rows evaluated : 560
  Features used  : ['close', 'sentiment_mean', 'news_count']
  Accuracy       : 0.8804  (88.0%)
==================================================

              precision    recall  f1-score   support

    Down (0)       0.79      0.97      0.87       235
      Up (1)       0.97      0.82      0.89       325

    accuracy                           0.88       560
   macro avg       0.88      0.89      0.88       560
weighted avg       0.90      0.88      0.88       560

✅ Good accuracy for a financial prediction model.


---

```
## Pipeline Schedule

The DAG is scheduled with `@weekly` — it runs automatically every Sunday at midnight and retrains the model from scratch using the most up-to-date data. Each new run overwrites the previous model file with a freshly trained version.

---

## Limitations — NYT RSS News Feed

The biggest limitation of this pipeline is the **NYT RSS feed**. RSS is designed as a "latest headlines" feed — it only returns the most recent **20 to 50 articles** at the time of fetching. It has no historical archive.

This means:
- For the ~560 trading days in the dataset (2024–2026), only articles from the **last few days** have real sentiment values
- The majority of training rows have `sentiment_mean=0` and `news_count=0` because no news was available for those historical dates
- As a result, the **sentiment feature is weak** across most of the dataset, and the model is primarily learning from gold price alone

**To fix this in a production version**, the NYT Article Search API would be used instead( which is not free). It allows querying articles by keyword and date range, making it possible to backfill two full years of war-related news sentiment. This would make `sentiment_mean` a genuinely meaningful feature across the entire training dataset.

---

## Notes on Model Accuracy

The 88% accuracy is higher than typical for financial prediction models. This is because:

1. The accuracy in `test_model.py` is evaluated on the **full dataset** (560 rows), not just the held-out test set
2. Gold prices followed a **strong upward trend** during 2024–2026, meaning the model can score well by frequently predicting UP
3. The `close` price feature alone carries most of the predictive power due to this trend

During training inside the DAG, a proper **80/20 chronological train/test split** with `shuffle=False` is applied to give an honest evaluation without data leakage.

---

## Bonus — Live Prediction for Tomorrow

> It is added to demonstrate how the trained model can be used in practice for live inference.

A separate script `predict_tomorrow.py` is subbmitted to show how the trained model makes a real prediction for the next trading day.

### How it works

1. Fetches **today's gold closing price** live from yfinance
2. Fetches **today's war news** from NYT RSS and computes live sentiment
3. Feeds both into the trained `gold_model.pkl`
4. Outputs whether gold is predicted to go **UP or DOWN** tomorrow with a confidence percentage

### Running it

```bash
python predict_tomorrow.py
```

### Example output

```
Today's gold close: $4432.30
War news sentiment: 0.006
War news count:     42

========================================
   TOMORROW'S GOLD PREDICTION
========================================
  Direction : ⬇️  DOWN
  Confidence: 72.0%
========================================
```

This demonstrates the full ML lifecycle — not just training the model but actually **using it** on unseen live data to make a real-world prediction.

---
**Gold API used:** yfinance `GC=F`
**Model accuracy:** 88%
**Notes:** NYT RSS only returns recent articles. Most historical rows have sentiment=0. A production version would use the NYT Article Search API to backfill historical sentiment data.

