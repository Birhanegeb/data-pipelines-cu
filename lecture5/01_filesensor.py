"""
Lecture 5 - Example 1: FileSensor

Based on listing_6_1 from "Data Pipelines with Apache Airflow" (Chapter 6).

FileSensor polls for a file or directory to exist. When the condition is met,
the sensor succeeds and downstream tasks can run.

Use case: Wait for data file before processing (e.g., supermarket promotions).
"""

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.filesystem.sensors.filesystem import FileSensor

dag = DAG(
    dag_id="lecture5_filesensor",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",  # Daily at 4pm
    tags=["lecture5", "sensors", "filesensor"],
)

# Wait for supermarket data file before processing
wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    filepath="/data/supermarket1/data.csv",
    poke_interval=60,  # Check every 60 seconds
    timeout=60 * 60 * 24,  # 24 hours max
    dag=dag,
)
