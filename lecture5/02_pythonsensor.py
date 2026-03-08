"""
Lecture 5 - Example 2: PythonSensor

Based on listing_6_2 from "Data Pipelines with Apache Airflow" (Chapter 6).

PythonSensor runs a custom callable that returns True/False. Use for complex
conditions (e.g., multiple files, _SUCCESS marker, API checks).
"""

from pathlib import Path

import airflow.utils.dates
from airflow import DAG

from airflow.sensors.python import PythonSensor

dag = DAG(
    dag_id="lecture5_pythonsensor",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    tags=["lecture5", "sensors", "pythonsensor"],
)


def _wait_for_supermarket(supermarket_id):
    """
    Check that both data files and _SUCCESS marker exist.
    Prevents processing partial uploads.
    """
    supermarket_path = Path("/data/" + supermarket_id)
    data_files = list(supermarket_path.glob("data-*.csv"))
    success_file = supermarket_path / "_SUCCESS"
    return len(data_files) > 0 and success_file.exists()


wait_for_supermarket_1 = PythonSensor(
    task_id="wait_for_supermarket_1",
    python_callable=_wait_for_supermarket,
    op_kwargs={"supermarket_id": "supermarket1"},
    poke_interval=60,
    timeout=60 * 60 * 24,
    dag=dag,
)
