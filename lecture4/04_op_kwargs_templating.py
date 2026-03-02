"""
Lecture 4 - Example 4: Templated op_kwargs

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

Values in op_kwargs are TEMPLATED before being passed to the callable.
This means we can pass Jinja strings and avoid extracting datetime components
inside the function - Airflow renders them at runtime.

Example: "year": "{{ execution_date.year }}" becomes "2019" when the task runs.
"""

from urllib import request

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator


def _get_data(year, month, day, hour, output_path, **_):
    """
    Download Wikipedia pageviews. All date components and output_path
    are passed in as already-rendered values from op_kwargs.
    """
    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )
    print(f"Downloading {url} to {output_path}")
    request.urlretrieve(url, output_path)


dag = DAG(
    dag_id="chapter4_op_kwargs_templating",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="@hourly",
    tags=["lecture4", "templating", "op_kwargs"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ execution_date.year }}",
        "month": "{{ execution_date.month }}",
        "day": "{{ execution_date.day }}",
        "hour": "{{ execution_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)
