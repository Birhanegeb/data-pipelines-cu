# Lecture 5: Supermarket Promotions Exercise

## Overview

This exercise implements an event-driven ETL pipeline for supermarket promotions data, using **FileSensor** from Chapter 6. The pipeline waits for data to appear, processes it, and loads it (with an empty `add_to_db` task for you to implement).

## Learning Objectives

By completing this exercise, you will:

1. **FileSensor** – Poll for file/directory existence before processing
2. **mode="reschedule"** – Avoid sensor deadlock by releasing slots between pokes
3. **Event-driven workflows** – Start processing when data is available, not on fixed schedule alone
4. **Pipeline pattern** – Sensor → Process → Load (add_to_db)
5. **Implement `add_to_db`** – Complete the empty task to load CSV into a database

## Exercise Structure

### Single DAG: `07_supermarket_exercise.py`

**Pipeline flow:**
```
wait_for_supermarket_1 → process_supermarket → add_to_db
```

| Task | Operator | Description |
|------|----------|-------------|
| `wait_for_supermarket_1` | FileSensor | Waits for `/data/supermarket1/_SUCCESS` before proceeding |
| `process_supermarket` | PythonOperator | Reads data-*.csv, aggregates promotions, saves to CSV |
| `add_to_db` | PythonOperator | **Empty – implement this task.** Load CSV into a database |

## Setup Instructions

### 1. Install Dependencies

```bash
pip install apache-airflow
# For FileSensor (Airflow 2.2+):
pip install apache-airflow-providers-filesystem
```

### 2. Create Data Directory and Test Data

```bash
mkdir -p /data/supermarket1/processed

# Create sample data and _SUCCESS marker
echo "product_id,promotion,date
P001,buy1get1,2024-01-15
P002,discount,2024-01-15" > /data/supermarket1/data-001.csv

echo "product_id,promotion,date
P001,buy1get1,2024-01-15
P003,discount,2024-01-15" > /data/supermarket1/data-002.csv

touch /data/supermarket1/_SUCCESS
```

### 3. Add DAG to Airflow

```bash
cp 07_supermarket_exercise.py /path/to/airflow/dags/
```

### 4. Enable the DAG

1. Open Airflow UI (e.g. http://localhost:8080)
2. Find `lecture5_supermarket_exercise`
3. Toggle it ON

## Running the Exercise

1. **Trigger manually**: Click the Play button on the DAG
2. **Or wait for schedule**: Runs daily at 16:00 (`0 16 * * *`)
3. Ensure `_SUCCESS` exists in `/data/supermarket1/` – the sensor will succeed and downstream tasks run

### Verifying Success

- Check task logs in Airflow UI
- Verify output: `ls /data/supermarket1/processed/`
- Output CSV format:

```csv
product_id,promotion_count,date
P001,2,2024-01-15
P002,1,2024-01-15
P003,1,2024-01-15
```

## How to Submit

### Submission Checklist

Submit a **Pull Request** that includes:

1. **Your DAG script(s)**
   - `07_supermarket_exercise.py` (or your completed/modified version)

2. **Output CSV file(s)**
   - At least one `promotions_YYYY-MM-DD.csv` from a successful run
   - Place in the `lecture5/` directory

3. **Screenshots (optional)**
   - Airflow Graph view showing successful run

### Pull Request Contents

```
lecture5/
├── 07_supermarket_exercise.py
├── promotions_2024-01-15.csv   # Your output (at least one run)
└── LECTURE5_EXERCISE_README.md
```

### PR Title Example

```
Lecture 5: Supermarket Promotions Exercise - [Your Name]
```

### PR Description Template

```markdown
## Lecture 5 Exercise Submission

- [x] DAG runs successfully
- [x] FileSensor waits for _SUCCESS
- [x] Process task produces CSV
- [ ] `add_to_db` task implemented (optional)

**Notes:** [Any issues or observations]
```

## Implement `add_to_db`

The `add_to_db` task is left empty for you to implement. You should:

1. Read the CSV from `/data/supermarket1/processed/promotions_{ds}.csv`
2. Insert rows into a database table with columns: `product_id`, `promotion_count`, `date`

**Options:**
- **SQLite** (no setup): Use Python's built-in `sqlite3`
- **Postgres**: Use `PostgresHook` from `apache-airflow-providers-postgres`

## Key Concepts Demonstrated

| Concept | Where Used |
|---------|------------|
| FileSensor | `wait_for_supermarket_1` – polls for _SUCCESS |
| mode="reschedule" | Avoids slot blocking during long waits |
| Event-driven | Pipeline starts when data appears |
