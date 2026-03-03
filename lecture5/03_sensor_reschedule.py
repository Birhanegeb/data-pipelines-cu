"""
Lecture 5 - Example 3: Sensor with mode="reschedule"

Based on Chapter 6 - avoiding sensor deadlock.

Default mode="poke": Sensor occupies a task slot while polling.
mode="reschedule": Sensor releases the slot between pokes – only uses slot
when actively checking. Prevents many waiting sensors from blocking other tasks.
"""

from pathlib import Path

import airflow.utils.dates
from airflow import DAG

from airflow.sensors.python import PythonSensor

dag = DAG(
    dag_id="lecture5_sensor_reschedule",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    max_active_runs=5,
    tags=["lecture5", "sensors", "reschedule"],
)


def _wait_for_supermarket(supermarket_id):
    path = Path("/data/" + supermarket_id)
    return (path / "_SUCCESS").exists()


wait_for_supermarket_1 = PythonSensor(
    task_id="wait_for_supermarket_1",
    python_callable=_wait_for_supermarket,
    op_kwargs={"supermarket_id": "supermarket1"},
    mode="reschedule",  # Release slot between pokes – avoids deadlock
    poke_interval=60,
    timeout=60 * 60 * 24,
    dag=dag,
)
