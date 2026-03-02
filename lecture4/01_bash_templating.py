"""
Lecture 4 - Example 1: BashOperator with Jinja Templating

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

Downloads Wikipedia pageviews using BashOperator. The URL is built dynamically
using Jinja templating with execution_date - no hardcoded dates!

URL format: https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/
            pageviews-{year}{month}{day}-{hour}0000.gz

The double curly braces {{ }} denote Jinja template variables that Airflow
renders at task execution time.
"""

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.bash import BashOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator

dag = DAG(
    dag_id="chapter4_bash_templating",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="@hourly",
    tags=["lecture4", "templating", "bash"],
)

get_data = BashOperator(
    task_id="get_data",
    bash_command=(
        "curl -sL -o /tmp/wikipageviews.gz "
        "'https://dumps.wikimedia.org/other/pageviews/"
        "{{ execution_date.year }}/"
        "{{ execution_date.year }}-{{ '%02d' % (execution_date.month,) }}/"
        "pageviews-{{ execution_date.year }}{{ '%02d' % (execution_date.month,) }}"
        "{{ '%02d' % (execution_date.day,) }}-"
        "{{ '%02d' % (execution_date.hour,) }}0000.gz'"
    ),
    dag=dag,
)
