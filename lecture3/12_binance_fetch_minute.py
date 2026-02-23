"""
Binance Price Fetcher - Minute Level
=====================================

This DAG fetches Bitcoin (BTCUSDT) average price from Binance API every minute
and saves the raw data to CSV files.

The data is saved with timestamps so it can be aggregated later by hourly and daily DAGs.

Schedule: Runs every minute
Start Date: Can be set to run for multiple days
"""

from datetime import datetime, timedelta
from pathlib import Path

import requests

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator # type: ignore
def _fetch_binance_price(**context):
    """
    Fetches Bitcoin price from Binance API and saves to CSV.
    
    API Response format:
    {
        "mins": 5,
        "price": "68285.81006621",
        "closeTime": 1771317380403
    }
    """
    api_url = "https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT"
    
    try:
        # Fetch data from Binance API
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        data['fetch_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert price to float for easier processing
        data['price_float'] = float(data['price'])
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        # Save to CSV with date partitioning
        date_str = datetime.now().strftime('%Y-%m-%d')
        hour_str = datetime.now().strftime('%H')
        minute_str = datetime.now().strftime('%M')
        
        output_dir = Path.home() / "airflow_data/binance/raw" / date_str
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual minute data
        output_file = output_dir / f"price_{hour_str}_{minute_str}.csv"
        df.to_csv(output_file, index=False)
        
        # Also append to daily file for easier aggregation
        daily_file = output_dir / "daily_raw.csv"
        if daily_file.exists():
            existing_df = pd.read_csv(daily_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(daily_file, index=False)
        
        print(f"Successfully fetched price: {data['price']} at {data['fetch_time']}")
        print(f"Saved to: {output_file}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Binance API: {e}")
        raise
    except Exception as e:
        print(f"Error processing data: {e}")
        raise


# DAG Definition
dag = DAG(
    dag_id="binance_fetch_minute",
    description="Fetches Bitcoin price from Binance every minute",
    schedule=timedelta(minutes=1),  # Run every minute
    start_date=datetime(2024, 1, 1),  # Start date - can run for multiple days
    catchup=False,  # Don't backfill - only run from now onwards
    tags=["binance", "crypto", "price", "minute"],
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=1),
    },
)

# Task: Fetch price
fetch_price = PythonOperator(
    task_id="fetch_binance_price",
    python_callable=_fetch_binance_price,
    dag=dag,
)

