# Lecture 4: StockSense Wikipedia Pageviews Exercise

## Overview

This exercise implements a complete ETL pipeline that fetches Wikipedia pageview data for tracked companies (Google, Amazon, Apple, Microsoft, Facebook) and saves the results to CSV. It demonstrates **Jinja templating**, **op_kwargs**, **templates_dict**, and **task context** from Lecture 4.

## Learning Objectives

By completing this exercise, you will:

1. **Jinja Templating**: Use `{{ execution_date }}` in operator arguments
2. **op_kwargs Templating**: Pass templated values to PythonOperator callables
3. **templates_dict**: Pass date-partitioned file paths to tasks
4. **Task Context**: Access `execution_date` and `ds` in Python functions
5. **ETL Pattern**: Extract (download) → Transform (parse/filter) → Load (save CSV)
6. **Implement `add_to_db`**: Complete the empty task to load CSV data into a database

## Exercise Structure

### Single DAG: `07_stocksense_exercise.py`

**Pipeline flow:**
```
get_data → extract_gz → fetch_pageviews → add_to_db
```

| Task | Operator | Description |
|------|----------|-------------|
| `get_data` | PythonOperator | Downloads Wikipedia pageviews .gz for execution hour (templated URL) |
| `extract_gz` | BashOperator | Extracts gzip to plain text |
| `fetch_pageviews` | PythonOperator | Parses file, filters for 5 companies, saves to CSV |
| `add_to_db` | PythonOperator | **Empty – implement this task.** Read CSV and insert into a database (SQLite, Postgres, etc.) |

**Data source:** https://dumps.wikimedia.org/other/pageviews/  
**Format:** `domain_code page_title view_count response_size` (space-separated)  
**Output:** `/data/stocksense/pageview_counts/{date}.csv`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install apache-airflow
# Optional: apache-airflow-providers-postgres (only if using Postgres variant)
```

### 2. Create Data Directory

```bash
mkdir -p /data/stocksense/pageview_counts
```

### 3. Add DAG to Airflow

Copy `07_stocksense_exercise.py` to your Airflow DAGs folder:

```bash
cp 07_stocksense_exercise.py /path/to/airflow/dags/
```

### 4. Enable the DAG

1. Open Airflow UI (e.g. http://localhost:8080)
2. Find `lecture4_stocksense_exercise`
3. Toggle it ON

## Running the Exercise

1. **Trigger manually** (recommended for first run): Click the Play button on the DAG
2. **Or wait for schedule**: Runs hourly (`@hourly`)
3. **Note:** Wikipedia pageviews are released ~45 min–3 hours after each hour. For recent hours, the download may fail (404). Use a few hours ago or enable catchup with a past start_date for testing.

### Verifying Success

- Check task logs in Airflow UI
- Verify output file: `ls /data/stocksense/pageview_counts/`
- Output CSV format:

```csv
pagename,pageviewcount,datetime
"Google",451,2024-01-15 10:00:00+00:00
"Amazon",9,2024-01-15 10:00:00+00:00
...
```

## How to Submit

### Submission Checklist

Submit a **Pull Request** that includes:

1. **Your DAG script(s)**
   - `07_stocksense_exercise.py` (or your completed/modified version)

2. **Output CSV file(s)**
   - At least one `pageview_counts_{date}.csv` from a successful run
   - Rename to: `pageview_counts_YYYY-MM-DD.csv` (e.g. `pageview_counts_2024-01-15.csv`)
   - Place in the `lecture4/` directory

3. **Screenshots (optional)**
   - Airflow Graph view showing successful run
   - Tree view with green tasks

### Pull Request Contents

```
lecture4/
├── 07_stocksense_exercise.py    # Your DAG
├── pageview_counts_2024-01-15.csv   # Your output (at least one run)
└── LECTURE4_EXERCISE_README.md  # This file
```

### PR Title Example

```
Lecture 4: StockSense Wikipedia Pageviews Exercise - [Your Name]
```

### PR Description Template

```markdown
## Lecture 4 Exercise Submission

- [x] DAG runs successfully
- [x] Output CSV generated
- [x] Templating (op_kwargs, templates_dict) used
- [ ] `add_to_db` task implemented (optional)

**Notes:** [Any issues or observations]
```

## Output File Format

| Column | Description | Example |
|--------|-------------|---------|
| pagename | Wikipedia page name | "Google" |
| pageviewcount | View count for that hour | 451 |
| datetime | Execution date/time | 2024-01-15 10:00:00+00:00 |

## Sample Output

A sample file `sample_output_pageview_counts.csv` is included to show the expected format. Your actual counts will vary by hour and date.

## Troubleshooting

### 404 on Wikipedia URL

Wikipedia pageviews appear with delay. Use `execution_date` from 2–4 hours ago, or enable catchup with a past `start_date`.

### FileNotFoundError: /tmp/wikipageviews

Ensure `extract_gz` runs before `fetch_pageviews`. Check task order and dependencies.

### Permission Denied on /data

Create the directory and ensure the Airflow process has write access:

```bash
mkdir -p /data/stocksense/pageview_counts
chmod 755 /data/stocksense
```

## Key Concepts Demonstrated

| Concept | Where Used |
|---------|------------|
| Jinja templating | `op_kwargs` for year, month, day, hour |
| execution_date | Injected into _fetch_pageviews |
| templates_dict | Date-partitioned output path `{{ ds }}.csv` |
| ETL pattern | Download → Extract → Transform → Load |

## Implement `add_to_db`

The `add_to_db` task is left empty for you to implement. You should:

1. Read the CSV from `context["templates_dict"]["output_path"]`
2. Insert rows into a database table with columns: `pagename`, `pageviewcount`, `datetime`

**Options:**
- **SQLite** (no setup): Use Python's built-in `sqlite3`
- **Postgres**: Use `PostgresOperator` or `PostgresHook` 
