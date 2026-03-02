# Lecture 4: Templating Tasks Using the Airflow Context

Based on **Chapter 4** of "Data Pipelines with Apache Airflow" by Bas P. Harenslak and Julian Rutger de Ruiter.

This lecture demonstrates how to use Airflow's templating mechanisms to dynamically inject variables (like execution dates) into your pipeline tasks at runtime.

## Overview

Templating allows you to write DAGs that work with any execution interval without hardcoding dates. Instead of static values, you use Jinja2 template expressions that Airflow evaluates when each task runs.

## Key Concepts

### 1. Jinja2 Templating
- Use double curly braces: `{{ variable_name }}`
- Available in operator arguments that support templating (see `template_fields`)
- Evaluated at **task execution time**, not at DAG load time

### 2. Task Context Variables
Common variables available in every task:

| Variable | Description | Example |
|----------|-------------|---------|
| `execution_date` | Start of the data interval | `pendulum.datetime` object |
| `next_execution_date` | End of the interval (start of next) | `pendulum.datetime` object |
| `ds` | execution_date as `YYYY-MM-DD` | `"2019-07-04"` |
| `ds_nodash` | execution_date as `YYYYMMDD` | `"20190704"` |
| `next_ds` | next_execution_date as `YYYY-MM-DD` | `"2019-07-05"` |
| `prev_ds` | Previous interval start | `"2019-07-03"` |
| `ts` | ISO8601 formatted execution_date | `"2019-07-04T00:00:00+00:00"` |
| `dag` | Current DAG object | DAG object |
| `task` | Current task/operator | Operator object |
| `ti` / `task_instance` | Current TaskInstance | TaskInstance object |

### 3. PythonOperator Exception
Unlike BashOperator (which takes a string that gets templated), PythonOperator takes a **function**. You access context via:
- `**kwargs` or `**context` in the function signature
- `op_kwargs` with templated strings (evaluated before passing to function)
- `templates_dict` for passing templated values into the function

## Examples

### 01_bash_templating.py
**BashOperator with Jinja templating** - Downloads Wikipedia pageviews using `execution_date` to build the URL dynamically.

- Uses `{{ execution_date.year }}`, `{{ execution_date.month }}`, etc.
- Demonstrates zero-padding: `{{ '{:02}'.format(execution_date.hour) }}`
- URL pattern: `pageviews-{year}{month}{day}-{hour}0000.gz`

### 02_print_context.py
**Inspecting task context** - Prints all available context variables to understand what Airflow provides at runtime.

- Use `**context` or `**kwargs` to capture all variables
- Run and check logs to see the full context dictionary

### 03_python_context.py
**PythonOperator with context** - Same Wikipedia download using PythonOperator.

- Access `execution_date` from `context["execution_date"]`
- Or use explicit argument: `def _get_data(execution_date, **context):`
- Python matches keyword argument names to pass values

### 04_op_kwargs_templating.py
**Templated op_kwargs** - Pass templated strings to PythonOperator via `op_kwargs`.

- Values in `op_kwargs` are **templated** before being passed to the callable
- Avoids extracting datetime components inside the function
- Example: `"year": "{{ execution_date.year }}"` → `"2019"` at runtime

### 05_templates_dict.py
**templates_dict for file paths** - Use `templates_dict` to pass templated paths to Python functions.

- `templates_dict` values are templated and passed in `context["templates_dict"]`
- Ideal for date-partitioned paths: `/data/{{ds}}.json`
- Access in function: `context["templates_dict"]["input_path"]`

### 07_stocksense_exercise.py (Exercise)
**Exercise DAG** - Complete ETL with CSV output. See `LECTURE4_EXERCISE_README.md` for instructions and submission.

### 06_stocksense_complete.py
**Complete StockSense DAG** - Full workflow from the book:
1. Download Wikipedia pageviews (BashOperator with templating)
2. Extract gzip file
3. Fetch pageview counts for tracked companies (Google, Amazon, Apple, Microsoft, Facebook)
4. Process and log results

## Inspecting Templated Values

### In Airflow UI
1. Run a task (or wait for it to be scheduled)
2. Click on the task in Graph or Tree view
3. Click **Rendered** (or **Rendered Template**) button
4. View the rendered values for templated fields

### Via CLI
```bash
airflow tasks render <dag_id> <task_id> <execution_date>
# Example:
airflow tasks render stocksense get_data 2019-07-19T00:00:00
```

This renders templates without running the task—useful for debugging.

## template_fields

Not all operator arguments support templating. Each operator defines `template_fields`—only those attributes are templated. Check the [Airflow docs](https://airflow.apache.org/docs/) for each operator's `template_fields`.

## Data Source: Wikipedia Pageviews

The examples use the [Wikimedia pageviews API](https://dumps.wikimedia.org/other/pageviews/):
- URL format: `https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{year}{month}{day}-{hour}0000.gz`
- Files are ~50MB gzipped (200–250MB uncompressed)
- Data is released ~45 minutes after each hour
- Format: `domain_code page_title view_count response_size` (space-separated)

## Usage

1. Copy DAG files to your Airflow `dags/` folder
2. Enable the DAG in the Airflow UI
3. Trigger manually or wait for schedule
4. For `02_print_context`, check task logs to see the printed context

## References

- Book: Data Pipelines with Apache Airflow (Manning), Chapter 4
- [Airflow Templating](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html#jinja-templating)
- [Wikipedia Pageviews](https://dumps.wikimedia.org/other/pageviews/)
