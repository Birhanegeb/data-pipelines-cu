"""
Lecture 4 - Example 6: Complete StockSense DAG

Based on Chapter 4 of "Data Pipelines with Apache Airflow".

StockSense: A (fictitious) stock market prediction tool using Wikipedia pageview
sentiment. Hypothesis: increase in company pageviews = positive sentiment = stock
likely to increase.

This DAG:
1. Downloads Wikipedia pageviews for the execution hour (BashOperator + templating)
2. Extracts the gzip file
3. Fetches pageview counts for tracked companies (Google, Amazon, Apple, Microsoft, Facebook)
4. Prints the results (in a full implementation, would write to Postgres)

Wikipedia pageviews format: domain_code page_title view_count response_size (space-separated)
"""

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}


def _fetch_pageviews(pagenames, **_):
    """
    Scan the extracted pageviews file and count views for each pagename.
    Format: domain_code page_title view_count response_size
    We filter for domain "en" (English Wikipedia) only.
    """
    result = dict.fromkeys(pagenames, 0)
    try:
        with open("/tmp/wikipageviews", "r") as f:
            for line in f:
                parts = line.strip().split(" ")
                if len(parts) >= 4:
                    domain_code, page_title, view_count, _ = parts[0], parts[1], parts[2], parts[3]
                    if domain_code == "en" and page_title in pagenames:
                        result[page_title] = int(view_count)
    except FileNotFoundError:
        print("File /tmp/wikipageviews not found - ensure extract_gz runs first")
        raise

    print(f"Pageview counts: {result}")
    return result


dag = DAG(
    dag_id="chapter4_stocksense_complete",
    start_date=airflow.utils.dates.days_ago(1),
    schedule="@hourly",
    catchup=False,
    tags=["lecture4", "templating", "stocksense"],
)

# Task 1: Download pageviews using templated URL
get_data = BashOperator(
    task_id="get_data",
    bash_command=(
        "curl -sL -o /tmp/wikipageviews.gz "
        "'https://dumps.wikimedia.org/other/pageviews/"
        "{{ execution_date.year }}/"
        "{{ execution_date.year }}-{{ '%02d' % (execution_date.month,) }}/"
        "pageviews-{{ execution_date.year }}{{ '%02d' % (execution_date.month,) }}"
        "{{ '%02d' % (execution_date.day,) }}-"
        "{{ '%02d' % (execution_date.hour,) }}0000.gz'"
    ),
    dag=dag,
)

# Task 2: Extract gzip (gunzip -f overwrites without prompting)
extract_gz = BashOperator(
    task_id="extract_gz",
    bash_command="gunzip -f /tmp/wikipageviews.gz",
    dag=dag,
)

# Task 3: Fetch pageview counts for tracked companies
fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": PAGENAMES},
    dag=dag,
)

get_data >> extract_gz >> fetch_pageviews
