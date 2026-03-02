"""
Lecture 4 - Example 3: PythonOperator with Task Context

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

Same Wikipedia pageviews download as 01_bash_templating, but using PythonOperator.
The PythonOperator doesn't take templated strings - it takes a function. We access
execution_date from the context (kwargs) that Airflow passes to our callable.

Two ways to receive execution_date:
1. context["execution_date"] - extract from the full context dict
2. def _get_data(execution_date, **context): - explicit argument (Python matches by name)
"""

from urllib import request

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator


def _get_data(execution_date, **_):
    """
    Download Wikipedia pageviews for the execution_date hour.
    Airflow passes execution_date as a keyword argument - we accept it explicitly.
    """
    year, month, day, hour, *_ = execution_date.timetuple()
    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:02d}/"
        f"pageviews-{year}{month:02d}{day:02d}-{hour:02d}0000.gz"
    )
    output_path = "/tmp/wikipageviews.gz"
    print(f"Downloading {url} to {output_path}")
    request.urlretrieve(url, output_path)


dag = DAG(
    dag_id="chapter4_python_context",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="@hourly",
    tags=["lecture4", "templating", "python"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    dag=dag,
)
