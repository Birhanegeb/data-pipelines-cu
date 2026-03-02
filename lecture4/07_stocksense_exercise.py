"""
Lecture 4 - Exercise: StockSense Wikipedia Pageviews ETL

Based on listing_4_20 from "Data Pipelines with Apache Airflow" (Chapter 4).

EXERCISE: Complete ETL pipeline that fetches Wikipedia pageviews for tracked
companies and saves to CSV. Uses Jinja templating for dynamic date handling.

Pipeline: get_data → extract_gz → fetch_pageviews → add_to_db

Data source: https://dumps.wikimedia.org/other/pageviews/
Format: domain_code page_title view_count response_size (space-separated)

Run for at least one successful execution, then include the output CSV in your PR.
"""

from pathlib import Path

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}
OUTPUT_DIR = "/data/stocksense/pageview_counts"


def _get_data(year, month, day, hour, output_path, **_):
    """Download Wikipedia pageviews for the given hour (templated op_kwargs)."""
    from urllib import request

    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )
    print(f"Downloading {url}")
    request.urlretrieve(url, output_path)


def _fetch_pageviews(pagenames, execution_date, **context):
    """
    Parse pageviews file, extract counts for tracked companies, save to CSV.
    execution_date is injected by Airflow from task context.
    output_path comes from templates_dict (date-partitioned path).
    """
    result = dict.fromkeys(pagenames, 0)
    with open("/tmp/wikipageviews", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                domain_code, page_title, view_count, _ = parts[0], parts[1], parts[2], parts[3]
                if domain_code == "en" and page_title in pagenames:
                    result[page_title] = int(view_count)

    output_path = context["templates_dict"]["output_path"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("pagename,pageviewcount,datetime\n")
        for pagename, count in result.items():
            f.write(f'"{pagename}",{count},{execution_date}\n')

    print(f"Saved pageview counts to {output_path}")
    print(f"Counts: {result}")
    return result


def _add_to_db(**context):
    """Add pageview counts to database. Implement this task."""
    pass


dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=airflow.utils.dates.days_ago(1),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["lecture4", "exercise", "stocksense", "etl"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ execution_date.year }}",
        "month": "{{ execution_date.month }}",
        "day": "{{ execution_date.day }}",
        "hour": "{{ execution_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)

extract_gz = BashOperator(
    task_id="extract_gz",
    bash_command="gunzip -f /tmp/wikipageviews.gz",
    dag=dag,
)

fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": PAGENAMES},
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

get_data >> extract_gz >> fetch_pageviews >> add_to_db
