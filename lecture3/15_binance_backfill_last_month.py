"""
Binance Backfill ETL - Last Month
==================================

This DAG backfills the last 30 days of Bitcoin price data using Binance's
historical klines API. It populates the same data structure as the live pipeline:
- Raw: /data/binance/raw/{date}/daily_raw.csv
- Hourly: /data/binance/hourly/{date}/hourly_avg.csv
- Daily: /data/binance/daily/daily_avg.csv

Schedule: Manual trigger only (or run once)
Uses: Binance klines API (historical OHLC data)
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 1000  # Max per request


def _fetch_klines(start_time_ms: int, end_time_ms: int) -> list:
    """Fetch klines from Binance API with pagination."""
    all_klines = []
    current_start = start_time_ms

    while current_start < end_time_ms:
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": current_start,
            "endTime": end_time_ms,
            "limit": LIMIT,
        }
        response = requests.get(BINANCE_KLINES_URL, params=params, timeout=30)
        response.raise_for_status()
        klines = response.json()

        if not klines:
            break

        all_klines.extend(klines)
        current_start = klines[-1][0] + 1  # Next millisecond after last candle

        if len(klines) < LIMIT:
            break

    return all_klines


def _klines_to_raw_format(klines: list) -> pd.DataFrame:
    """
    Convert Binance klines to raw format matching the live pipeline.
    Klines: [openTime, open, high, low, close, volume, closeTime, ...]
    """
    records = []
    for k in klines:
        open_time_ms = k[0]
        close_time_ms = k[6]
        # Use close price (or (high+low)/2 for typical price)
        price = float(k[4])  # close
        dt = datetime.fromtimestamp(open_time_ms / 1000)

        records.append({
            "mins": 1,  # 1-minute kline
            "price": str(price),
            "closeTime": close_time_ms,
            "timestamp": dt.isoformat(),
            "fetch_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "price_float": price,
        })
    return pd.DataFrame(records)


def _backfill_last_month(**context):
    """
    Full ETL: Fetch last 30 days from Binance klines, then populate
    raw, hourly, and daily aggregations.
    """
    now = datetime.now()
    end_date = now.date()
    start_date = end_date - timedelta(days=30)

    start_time_ms = int(datetime(start_date.year, start_date.month, start_date.day).timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)

    print(f"Backfilling from {start_date} to {end_date}")
    print(f"Fetching klines from Binance API...")

    # 1. Extract: Fetch historical klines
    klines = _fetch_klines(start_time_ms, end_time_ms)
    if not klines:
        print("No klines data received.")
        return

    raw_df = _klines_to_raw_format(klines)
    raw_df["fetch_time"] = pd.to_datetime(raw_df["fetch_time"])
    raw_df["date"] = raw_df["fetch_time"].dt.strftime("%Y-%m-%d")
    raw_df["hour"] = raw_df["fetch_time"].dt.strftime("%H")

    print(f"Fetched {len(raw_df)} data points")

    # 2. Transform & Load: Write raw data by date
    base_raw = Path("/data/binance/raw")
    base_hourly = Path("/data/binance/hourly")
    base_daily = Path("/data/binance/daily")
    base_daily.mkdir(parents=True, exist_ok=True)

    daily_dfs = []

    for date_str, day_df in raw_df.groupby("date"):
        # Raw: append/merge with existing
        raw_dir = base_raw / date_str
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_file = raw_dir / "daily_raw.csv"

        day_raw = day_df.drop(columns=["date", "hour"])
        if raw_file.exists():
            existing = pd.read_csv(raw_file)
            existing["fetch_time"] = pd.to_datetime(existing["fetch_time"])
            combined = pd.concat([existing, day_raw], ignore_index=True)
            combined = combined.drop_duplicates(subset=["closeTime"], keep="last")
            combined = combined.sort_values("fetch_time")
        else:
            combined = day_raw

        combined.to_csv(raw_file, index=False)

        # Hourly aggregation for this day
        hourly_records = []
        for hour_str, hour_df in day_df.groupby("hour"):
            hourly_records.append({
                "date": date_str,
                "hour": hour_str,
                "avg_price": hour_df["price_float"].mean(),
                "min_price": hour_df["price_float"].min(),
                "max_price": hour_df["price_float"].max(),
                "first_price": hour_df["price_float"].iloc[0],
                "last_price": hour_df["price_float"].iloc[-1],
                "data_points": len(hour_df),
                "calculated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            })

        if hourly_records:
            hourly_df = pd.DataFrame(hourly_records)
            hourly_dir = base_hourly / date_str
            hourly_dir.mkdir(parents=True, exist_ok=True)
            hourly_file = hourly_dir / "hourly_avg.csv"
            hourly_df.to_csv(hourly_file, index=False)

            # Daily aggregation for this day
            daily_stats = {
                "date": date_str,
                "avg_price": hourly_df["avg_price"].mean(),
                "min_price": hourly_df["min_price"].min(),
                "max_price": hourly_df["max_price"].max(),
                "opening_price": hourly_df["first_price"].iloc[0],
                "closing_price": hourly_df["last_price"].iloc[-1],
                "price_change": 0,
                "price_change_pct": 0,
                "total_data_points": hourly_df["data_points"].sum(),
                "hours_with_data": len(hourly_df),
                "calculated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            }
            opening = daily_stats["opening_price"]
            if opening > 0:
                daily_stats["price_change"] = daily_stats["closing_price"] - opening
                daily_stats["price_change_pct"] = (daily_stats["price_change"] / opening) * 100

            daily_dfs.append(pd.DataFrame([daily_stats]))

    # 3. Merge daily into daily_avg.csv
    if daily_dfs:
        new_daily = pd.concat(daily_dfs, ignore_index=True)
        daily_file = base_daily / "daily_avg.csv"

        if daily_file.exists():
            existing_daily = pd.read_csv(daily_file)
            existing_dates = set(existing_daily["date"].astype(str))
            new_dates = set(new_daily["date"].astype(str))
            existing_daily = existing_daily[~existing_daily["date"].isin(new_dates)]
            combined_daily = pd.concat([existing_daily, new_daily], ignore_index=True)
        else:
            combined_daily = new_daily

        combined_daily = combined_daily.sort_values("date")
        combined_daily.to_csv(daily_file, index=False)
        print(f"Backfill complete. {len(daily_dfs)} days added to {daily_file}")

    print(f"Backfill finished. Processed {raw_df['date'].nunique()} days.")


# DAG: manual trigger, run once for backfill
dag = DAG(
    dag_id="binance_backfill_last_month",
    description="Backfills last 30 days of Binance BTC price data using historical klines",
    schedule=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "price", "backfill", "etl"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)

backfill_task = PythonOperator(
    task_id="backfill_last_month",
    python_callable=_backfill_last_month,
    dag=dag,
)
