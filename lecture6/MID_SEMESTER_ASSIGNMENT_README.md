# Lecture 6: Mid-Semester Assignment

## Gold Price & War News ML Pipeline

Build an **ETL + ML pipeline** that:
1. Fetches **gold prices** (2024 to today) from any API
2. Fetches **war-related news** from [NYT RSS](https://www.nytimes.com/rss)
3. Trains an **ML model** to predict if gold price will go **up or down** based on news sentiment
4. Runs **weekly** to deploy a new model

## Learning Objectives

- ETL with Apache Airflow (scheduled workflows)
- External APIs (gold price) and RSS feeds (NYT)
- Sentiment analysis on text
- ML classification (up/down prediction)
- Model persistence and testing

---

## Assignment Requirements

### 1. Data Sources

| Source | Requirement |
|--------|-------------|
| **Gold price** | Any API – e.g. yfinance (`GC=F`), goldapi.io, metals.live. Date range: 2024-01-01 to today. |
| **War news** | NYT RSS – use feeds from [https://www.nytimes.com/rss](https://www.nytimes.com/rss). Filter for war/conflict-related articles. |

### 2. Pipeline Tasks

```
fetch_gold_prices → compute_sentiment_and_merge ← fetch_war_news
                          ↓
                    train_model
```

- **fetch_gold_prices**: Download gold prices from 2024 to today
- **fetch_war_news**: Fetch NYT RSS, filter war-related items
- **compute_sentiment_and_merge**: Sentiment on news, merge with gold prices, create target (1=up, 0=down)
- **train_model**: Train classifier, save model file

### 3. Schedule

- ETL must run **every week** (`@weekly`) to deploy a new model
- Use Airflow `schedule="@weekly"` or `schedule="0 0 * * 0"`

### 4. Deliverables

| Deliverable | Description |
|-------------|-------------|
| **ETL script(s)** | DAG(s) that run the full pipeline |
| **Model file** | Trained model (e.g. `.pkl`, `.joblib`) |
| **Sample data** | Small sample of `gold_prices.csv`, `war_news.csv`, `training_data.csv` |
| **Testing script** | `test_model.py` to load and test the model |

### 5. Deadline
- 24/3/2026

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# Or manually:
pip install apache-airflow yfinance feedparser pandas scikit-learn textblob
```

### 2. Create Data Directory

```bash
mkdir -p /data/gold_war_pipeline/models
```

### 3. Add DAG to Airflow

```bash
cp gold_war_etl_dag.py /path/to/airflow/dags/
```

Or set `DATA_DIR` in the DAG to a path your Airflow worker can write to.

### 4. Run the Pipeline

1. Trigger manually in Airflow UI
2. Or wait for schedule (`@weekly`)
3. Output files:
   - `gold_prices.csv`
   - `war_news.csv`
   - `training_data.csv`
   - `models/gold_model.pkl`

### 5. Test the Model

```bash
python test_model.py --model /data/gold_war_pipeline/models/gold_model.pkl --data /data/gold_war_pipeline
```

---

## Data Formats

### gold_prices.csv

| Column | Description |
|--------|-------------|
| date | YYYY-MM-DD |
| open | Opening price |
| high | High price |
| low | Low price |
| close | Closing price |

### war_news.csv

| Column | Description |
|--------|-------------|
| date | Publication date (YYYY-MM-DD) |
| title | Article title |
| summary | Article summary |

### training_data.csv

| Column | Description |
|--------|-------------|
| date | Trading date |
| close | Gold closing price |
| sentiment_mean | Mean sentiment of war news that day |
| news_count | Number of war-related articles |
| target | 1 = next-day price up, 0 = down |

---

## How to Submit

### Submission Checklist

Submit a **Pull Request** with:

1. **ETL script(s)**
   - `gold_war_etl_dag.py` (or your modified version)

2. **Model file**
   - `gold_model.pkl` (or `.joblib`) – the trained model

3. **Sample data files** (small samples, not full datasets)
   - `gold_prices_sample.csv` (e.g. first 20 rows)
   - `war_news_sample.csv` (e.g. first 20 rows)
   - `training_data_sample.csv` (e.g. first 20 rows)

4. **Testing script**
   - `test_model.py` – loads model and reports accuracy

### Pull Request Structure

```
lecture6/
├── gold_war_etl_dag.py      # Your ETL DAG
├── test_model.py            # Model testing script
├── gold_model.pkl           # Trained model
├── gold_prices_sample.csv   # Sample gold data
├── war_news_sample.csv      # Sample news data
├── training_data_sample.csv # Sample training data
├── MID_SEMESTER_ASSIGNMENT_README.md
└── requirements.txt
```

### PR Title Example

```
Lecture 6: Mid-Semester Assignment - Gold & War ML Pipeline - [Your Name]
```

### PR Description Template

```markdown
## Mid-Semester Assignment Submission

- [x] ETL fetches gold prices (2024–today)
- [x] ETL fetches war-related news from NYT RSS
- [x] Sentiment computed and merged with gold prices
- [x] ML model trained and saved
- [x] Pipeline scheduled weekly
- [x] test_model.py runs successfully

**Gold API used:** [e.g. yfinance GC=F]
**Model accuracy (sample):** [e.g. 0.58]

**Notes:** [Any issues or observations]
```

---

## NYT RSS Feeds

[RSS Feeds - The New York Times](https://www.nytimes.com/rss)

Relevant feeds for war/conflict news:
- World: `https://rss.nytimes.com/services/xml/rss/nyt/World.xml`
- Home: `https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml`

Filter items by keywords: `war`, `conflict`, `attack`, `military`, `invasion`, etc.

**Terms:** Use only for personal/non-commercial work. See [NYT Terms](https://www.nytimes.com/rss) for attribution requirements.

---

## Alternative Gold APIs

| API | Notes |
|-----|-------|
| **yfinance** | Free, no key. Use `GC=F` (gold futures) |
| **goldapi.io** | Free tier, requires API key |
| **metals.live** | Free tier available |

---

## Troubleshooting

### No gold data
- yfinance: Ensure symbol `GC=F` is correct; check date range
- Other APIs: Verify API key and rate limits

### No war news
- Check NYT RSS URLs
- Broaden keyword filter if needed

### Model accuracy low
- Add more features (e.g. lagged sentiment, price changes)
- Try different classifiers
- Use train/test split and report both

### Permission denied on /data
- Use a directory under your home or project
- Set `DATA_DIR` in the DAG accordingly
