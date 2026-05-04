from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import requests
import json
import subprocess

# ---------------------------
# TASK 1: Fetch Weather API
# ---------------------------
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=53.08&longitude=8.80&current_weather=true"

    response = requests.get(url)
    print("Status code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("Data received:", data)

        if data:
            with open("/tmp/weather_raw.json", "w") as f:
                json.dump(data, f, indent=4)
            print("Weather data saved!")
        else:
            print("ERROR: Empty JSON response")
    else:
        raise Exception("API request failed")


# ---------------------------
# TASK 2: Ollama Normalization
# ---------------------------
def normalize_weather():
    with open("/tmp/weather_raw.json") as f:
        data = json.load(f)

    prompt = f"""
You are a data transformation engine.

Convert the input weather JSON into STRICT VALID JSON ONLY.

Rules:
- Output ONLY JSON
- No explanations
- No markdown
- No text before or after
- Keep numeric values as numbers
- Flatten nested objects

Input:
{data}
"""

    response = requests.post(
        "http://10.0.2.2:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )

    result = response.json()

    clean_json = json.loads(result["response"])

    with open("/tmp/weather_normalized.json", "w") as f:
        json.dump(clean_json, f, indent=4)

    print("Strict JSON saved!")


# ---------------------------
# TASK 3: Spark ETL
# ---------------------------
def spark_etl():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("WeatherETL").getOrCreate()

    df = spark.read.option("multiline", "true").json("/tmp/weather_normalized.json")

    df.printSchema()

    flat_df = df.select(
        "latitude",
        "longitude",
        "elevation",
        "timezone",
        df.current_weather.temperature.alias("temperature"),
        df.current_weather.windspeed.alias("windspeed"),
        df.current_weather.winddirection.alias("winddirection"),
        df.current_weather.time.alias("time")
    )

    flat_df.show()

    flat_df.write.mode("overwrite").option("header", "true").csv("/tmp/weather_curated")

    spark.stop()


# ---------------------------
# DAG DEFINITION
# ---------------------------
with DAG(
    dag_id="weather_full_inline_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,   # manual trigger only
    catchup=False,
    tags=["weather", "etl", "spark", "ollama"]
) as dag:

    task_fetch = PythonOperator(
        task_id="fetch_weather",
        python_callable=fetch_weather
    )

    task_ollama = PythonOperator(
        task_id="normalize_weather",
        python_callable=normalize_weather
    )

    task_spark = PythonOperator(
        task_id="spark_etl",
        python_callable=spark_etl
    )

    # ---------------------------
    # Dependency Flow
    # ---------------------------
    task_fetch >> task_ollama >> task_spark