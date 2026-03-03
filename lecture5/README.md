# Lecture 5: Triggering Workflows & Communicating with External Systems

Based on **Chapters 6 and 7** of "Data Pipelines with Apache Airflow" by Bas P. Harenslak and Julian Rutger de Ruiter.

## Overview

This lecture covers event-driven workflow triggers (sensors, DAG-to-DAG) and connecting Airflow to external systems (cloud, databases, APIs).

## Chapter 6: Triggering Workflows

- **Sensors** – Poll for conditions (files, data availability)
- **TriggerDagRunOperator** – One DAG triggers another
- **ExternalTaskSensor** – Wait for another DAG's task to complete
- **REST/CLI** – Trigger DAGs from outside Airflow

## Chapter 7: Communicating with External Systems

- **Operators** – Interface to cloud services (AWS, GCP, Azure)
- **Hooks** – Low-level connection abstractions
- **Provider packages** – `apache-airflow-providers-amazon`, etc.

## Examples

| File | Description | Source |
|------|-------------|--------|
| `01_filesensor.py` | FileSensor – wait for file to exist | listing_6_1 |
| `02_pythonsensor.py` | PythonSensor – custom condition | listing_6_2 |
| `03_sensor_reschedule.py` | PythonSensor with `mode="reschedule"` – avoid deadlock | Ch 6 |
| `04_trigger_dag_run.py` | TriggerDagRunOperator – trigger downstream DAG | figure_6_17 |
| `05_external_task_sensor.py` | ExternalTaskSensor – wait for another DAG | figure_6_19 |
| `06_external_task_sensor_delta.py` | ExternalTaskSensor with `execution_delta` | figure_6_20 |

## Exercise

See `LECTURE5_EXERCISE_README.md` for the supermarket promotions exercise.

## Dependencies

```bash
pip install apache-airflow
# For sensors (filesystem):
pip install apache-airflow-providers-filesystem
# For external systems (optional):
pip install apache-airflow-providers-amazon
pip install apache-airflow-providers-postgres
```

## Reference

- Book: Data Pipelines with Apache Airflow (Manning), Chapters 6–7
