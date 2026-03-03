"""
Lecture 5 - Example 5: ExternalTaskSensor

Based on figure_6_19 from "Data Pipelines with Apache Airflow" (Chapter 6).

ExternalTaskSensor polls another DAG's task state. Use when DAG 4 must wait
for DAGs 1, 2, 3 to all complete (e.g., aggregate report after 3 ETL pipelines).

DAG 4 "pulls" execution – it schedules itself and waits for upstream DAGs.
"""

import airflow.utils.dates
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

# DAGs 1, 2, 3: Independent ETL pipelines
for i in range(1, 4):
    d = DAG(
        dag_id=f"lecture5_external_sensor_dag{i}",
        start_date=airflow.utils.dates.days_ago(3),
        schedule="0 0 * * *",
        tags=["lecture5", "external_task_sensor"],
    )
    EmptyOperator(task_id="etl", dag=d)

# DAG 4: Report – waits for all three ETL DAGs to complete
dag4 = DAG(
    dag_id="lecture5_external_sensor_dag4",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 0 * * *",  # Same schedule as DAGs 1–3 for alignment
    tags=["lecture5", "external_task_sensor"],
)

wait_tasks = [
    ExternalTaskSensor(
        task_id=f"wait_for_dag{i}_etl",
        external_dag_id=f"lecture5_external_sensor_dag{i}",
        external_task_id="etl",
        dag=dag4,
    )
    for i in range(1, 4)
]

report = EmptyOperator(task_id="report", dag=dag4)

wait_tasks >> report
