"""
Lecture 5 - Exercise: Supermarket Promotions ETL with FileSensor

Based on Chapter 6 "Triggering Workflows" – supermarket data ingestion pattern.

EXERCISE: Complete pipeline that waits for supermarket data (FileSensor),
processes it, and loads to a database. The add_to_db task is left empty.

Pipeline: wait_for_supermarket_1 → process_supermarket → add_to_db
"""

import airflow.utils.dates
from airflow import DAG
from pathlib import Path
import sqlite3
import csv
try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.filesystem.sensors.filesystem import FileSensor

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator

DATA_DIR = "/data/supermarket1"


def _process_supermarket(**context):
    """
    Read raw data from supermarket, aggregate promotions, save to CSV.
    execution_date (ds) comes from Airflow context.
    """
    import csv
    from pathlib import Path

    ds = context["ds"]
    output_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read all data-*.csv files and aggregate
    raw_dir = Path(DATA_DIR)
    data_files = list(raw_dir.glob("data-*.csv"))
    if not data_files:
        raise FileNotFoundError(f"No data-*.csv files in {raw_dir}")

    promotions = {}
    for f in data_files:
        with open(f, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                prod = row.get("product_id", row.get("product", "unknown"))
                promotions[prod] = promotions.get(prod, 0) + 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "promotion_count", "date"])
        for prod, count in promotions.items():
            writer.writerow([prod, count, context["ds"]])

    print(f"Saved to {output_path}: {len(promotions)} products")
    return output_path


def _add_to_db(**context):
    """Add promotions to SQLite database."""
    ti = context['ti']  # TaskInstance
    csv_path = ti.xcom_pull(task_ids='process_supermarket')
    if not csv_path:
        raise FileNotFoundError("No CSV file path found from process_supermarket task")
    csv_path = Path(csv_path)
    db_path = csv_path.parent / "supermarket.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotions (
            product_id TEXT,
            promotion_count INTEGER,
            date TEXT
        )
    """)
    # Read CSV and insert into DB
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO promotions (product_id, promotion_count, date) VALUES (?, ?, ?)",
                (row['product_id'], int(row['promotion_count']), row['date'])
            )
    conn.commit()
    conn.close()
    print(f"Inserted promotions from {csv_path} into database {db_path}")
dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

# Wait for supermarket data (FileSensor checks for _SUCCESS marker)
wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    filepath=f"{DATA_DIR}/_SUCCESS",
    poke_interval=60,
    timeout=60 * 60 * 24,
    mode="reschedule",
    dag=dag,
)

process_supermarket = PythonOperator(
    task_id="process_supermarket",
    python_callable=_process_supermarket,
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    dag=dag,
)

wait_for_supermarket_1 >> process_supermarket >> add_to_db
