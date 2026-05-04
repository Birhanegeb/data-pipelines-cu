# Weather ETL Pipeline (Airflow + Spark + Ollama)
The pipeline consists of the following stages:

### 1. Data Ingestion (Task A)

* Weather data is fetched from the Open-Meteo API.
* The raw response is stored locally as `weather_raw.json`.

### 2. Data Normalization (Task B)

* Ollama is used to transform and normalize raw or semi-structured JSON data.
* The output is stored as `weather_normalized.json`.

### 3. Data Processing (Task C)

* Apache Spark is used to process and transform the JSON data.
* Nested JSON structures are flattened into a tabular format.
* Key fields such as latitude, longitude, temperature, windspeed, winddirection, and time are extracted.

### 4. Data Output (Task D)

* The processed dataset is written as a CSV file.
* Spark outputs the data in partitioned format inside the `weather_curated/` directory.
* Includes `part-*.csv` files and a `_SUCCESS` marker.

---

## Workflow Orchestration

The entire pipeline is orchestrated using Apache Airflow.

The DAG structure follows:

```
Fetch Weather Data → Ollama Processing → Spark ETL → Output Validation
```

Airflow manages task dependencies, execution order, and monitoring.

```


