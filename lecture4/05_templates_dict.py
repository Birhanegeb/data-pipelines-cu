"""
Lecture 4 - Example 5: templates_dict for Templated Paths

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

templates_dict allows passing templated values to PythonOperator. The values
are rendered at runtime and available in context["templates_dict"].

Use case: Date-partitioned file paths like /data/events/{{ds}}.json
"""

from pathlib import Path

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator


def _process_data(**context):
    """
    Process data using paths from templates_dict.
    Access via context["templates_dict"]["key_name"]
    """
    input_path = context["templates_dict"]["input_path"]
    output_path = context["templates_dict"]["output_path"]
    ds = context["templates_dict"]["ds"]

    print(f"Processing data for date: {ds}")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")

    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Simulate processing - in real pipeline you'd read/transform/write
    with open(output_path, "w") as f:
        f.write(f"Processed data for {ds}\n")
        f.write(f"Input was: {input_path}\n")


dag = DAG(
    dag_id="chapter4_templates_dict",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="@daily",
    tags=["lecture4", "templating", "templates_dict"],
)

process_data = PythonOperator(
    task_id="process_data",
    python_callable=_process_data,
    templates_dict={
        "input_path": "/data/input/{{ ds }}.json",
        "output_path": "/data/output/{{ ds }}.csv",
        "ds": "{{ ds }}",
    },
    dag=dag,
)
