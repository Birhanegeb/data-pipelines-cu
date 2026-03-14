# Lecture 6: Mid-Semester Assignment

## Gold Price & War News ML Pipeline

This assignment combines **ETL**, **sentiment analysis**, and **ML** to predict gold price direction based on war-related news from The New York Times RSS feeds.

## Overview

- **Data sources:** Gold price API + [NYT RSS](https://www.nytimes.com/rss) (war-related news)
- **Date range:** 2024 to today
- **Task:** Predict if gold price will go up or down based on news sentiment
- **Schedule:** ETL runs weekly to deploy a new model
- **Submission:** ETL scripts, model file, sample data, testing script (same format as Lecture 5)

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run ETL manually or add DAG to Airflow
3. Run test: `python test_model.py --model models/gold_model.pkl --data data/`
4. Submit: ETL + model + data + test script via Pull Request

## Full Instructions

See **MID_SEMESTER_ASSIGNMENT_README.md** for setup, data formats, and submission checklist.
