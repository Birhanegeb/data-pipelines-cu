"""
Binance Price Aggregator - Hourly Average
==========================================

This DAG calculates hourly average Bitcoin price from the minute-level data
collected by the binance_fetch_minute DAG.

Schedule: Runs every hour
Reads: /data/binance/raw/{date}/daily_raw.csv
Writes: /data/binance/hourly/{date}/hourly_avg.csv
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator#type: ignore


def _calculate_hourly_average(**context):
    """
    Calculates hourly average price from minute-level data.
    Reads the daily raw CSV file and aggregates by hour.
    """
    # Get current date and previous hour
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_hour = now.strftime('%H')
    
    # Path to raw data
    raw_file = Path.home() / "airflow_data/binance/raw" / current_date / "daily_raw.csv"    
    if not raw_file.exists():
        print(f"No raw data file found at {raw_file}")
        print("Waiting for minute-level data to be collected...")
        return
    
    try:
        # Read raw data
        df = pd.read_csv(raw_file)
        
        # Convert timestamp to datetime
        df['fetch_time'] = pd.to_datetime(df['fetch_time'])
        
        # Extract hour from timestamp
        df['hour'] = df['fetch_time'].dt.strftime('%H')
        
        # Filter for current hour
        current_hour_data = df[df['hour'] == current_hour].copy()
        
        if current_hour_data.empty:
            print(f"No data found for hour {current_hour}")
            return
        
        # Calculate statistics for the hour
        hourly_stats = {
            'date': current_date,
            'hour': current_hour,
            'avg_price': current_hour_data['price_float'].mean(),
            'min_price': current_hour_data['price_float'].min(),
            'max_price': current_hour_data['price_float'].max(),
            'first_price': current_hour_data['price_float'].iloc[0],
            'last_price': current_hour_data['price_float'].iloc[-1],
            'data_points': len(current_hour_data),
            'calculated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Create DataFrame
        hourly_df = pd.DataFrame([hourly_stats])
        
        # Save to CSV
        output_dir = Path.home() / "airflow_data/binance/hourly" / current_date
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "hourly_avg.csv"
        
        # Append if file exists
        if output_file.exists():
            existing_df = pd.read_csv(output_file)
            # Remove duplicate hour if exists
            existing_df = existing_df[existing_df['hour'] != current_hour]
            hourly_df = pd.concat([existing_df, hourly_df], ignore_index=True)
        
        hourly_df.to_csv(output_file, index=False)
        
        print(f"Hourly average calculated for {current_date} hour {current_hour}:")
        print(f"  Average Price: ${hourly_stats['avg_price']:.2f}")
        print(f"  Min Price: ${hourly_stats['min_price']:.2f}")
        print(f"  Max Price: ${hourly_stats['max_price']:.2f}")
        print(f"  Data Points: {hourly_stats['data_points']}")
        print(f"  Saved to: {output_file}")
        
        return hourly_stats
        
    except Exception as e:
        print(f"Error calculating hourly average: {e}")
        raise


# DAG Definition
dag = DAG(
    dag_id="binance_calculate_hourly",
    description="Calculates hourly average Bitcoin price from minute data",
    schedule=timedelta(hours=1),  # Run every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "price", "hourly", "aggregation"],
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
)

# Task: Calculate hourly average
calculate_hourly = PythonOperator(
    task_id="calculate_hourly_average",
    python_callable=_calculate_hourly_average,
    dag=dag,
)

