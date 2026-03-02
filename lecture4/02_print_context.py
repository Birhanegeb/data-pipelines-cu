"""
Lecture 4 - Example 2: Printing the Task Context

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

This DAG prints all available task context variables. Run it and check the task
logs to see what Airflow provides at runtime.

Useful for understanding: ds, next_ds, execution_date, task_instance, etc.
"""

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator


def _print_context(**kwargs):
    """Print all task context variables passed by Airflow."""
    print("=== Task Context Variables ===")
    for key, value in sorted(kwargs.items()):
        if key not in ("dag", "task", "ti", "task_instance", "conf", "macros"):
            print(f"  {key}: {value}")
    print("\n=== Key variables ===")
    print(f"  execution_date: {kwargs.get('execution_date')}")
    print(f"  next_execution_date: {kwargs.get('next_execution_date')}")
    print(f"  ds (execution date as YYYY-MM-DD): {kwargs.get('ds')}")
    print(f"  next_ds: {kwargs.get('next_ds')}")
    print(f"  ds_nodash: {kwargs.get('ds_nodash')}")
    print(f"  run_id: {kwargs.get('run_id')}")


dag = DAG(
    dag_id="chapter4_print_context",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="@daily",
    tags=["lecture4", "templating", "context"],
)

print_context = PythonOperator(
    task_id="print_context",
    python_callable=_print_context,
    dag=dag,
)
