"""
Lecture 5 - Example 6: ExternalTaskSensor with execution_delta

Based on figure_6_20 from "Data Pipelines with Apache Airflow" (Chapter 6).

When DAGs have different schedule_interval, execution dates don't align.
Use execution_delta to look back in time for the upstream task.

Example: DAG1 runs at 16:00, DAG2 runs at 22:00. DAG2 checks for DAG1's
task from 6 hours earlier: execution_delta=timedelta(hours=6).
"""

import datetime

import airflow.utils.dates
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

# DAG 1: Runs at 16:00 daily
dag1 = DAG(
    dag_id="lecture5_external_delta_dag1",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    tags=["lecture5", "external_task_sensor", "execution_delta"],
)

copy_to_raw = EmptyOperator(task_id="copy_to_raw", dag=dag1)
process = EmptyOperator(task_id="process_supermarket", dag=dag1)
copy_to_raw >> process

# DAG 2: Runs at 22:00 daily – 6 hours after DAG 1
dag2 = DAG(
    dag_id="lecture5_external_delta_dag2",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 22 * * *",
    tags=["lecture5", "external_task_sensor", "execution_delta"],
)

wait = ExternalTaskSensor(
    task_id="wait_for_process_supermarket",
    external_dag_id="lecture5_external_delta_dag1",
    external_task_id="process_supermarket",
    execution_delta=datetime.timedelta(hours=6),  # Look back 6h for alignment
    dag=dag2,
)

report = EmptyOperator(task_id="report", dag=dag2)
wait >> report
