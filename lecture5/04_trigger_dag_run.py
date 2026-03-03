"""
Lecture 5 - Example 4: TriggerDagRunOperator

Based on figure_6_17 from "Data Pipelines with Apache Airflow" (Chapter 6).

One DAG triggers another. Useful for splitting workflows – DAG 1 does ETL,
DAG 2 does reporting. Triggered DAG can have schedule_interval=None.
"""

import airflow.utils.dates
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# DAG 1: Ingests data, then triggers DAG 2
dag1 = DAG(
    dag_id="lecture5_trigger_example_dag1",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 0 * * *",
    tags=["lecture5", "trigger"],
)

etl = EmptyOperator(task_id="etl", dag=dag1)

trigger_dag2 = TriggerDagRunOperator(
    task_id="trigger_report_dag",
    trigger_dag_id="lecture5_trigger_example_dag2",
    dag=dag1,
)

etl >> trigger_dag2

# DAG 2: Report – only runs when triggered by DAG 1
dag2 = DAG(
    dag_id="lecture5_trigger_example_dag2",
    start_date=airflow.utils.dates.days_ago(3),
    schedule=None,  # Only runs when triggered
    tags=["lecture5", "trigger"],
)

report = EmptyOperator(task_id="report", dag=dag2)
