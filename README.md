# Weather–Ridership Data Pipeline

Automated batch pipeline: ingests weather + ridership data daily, validates
and transforms it through bronze/silver/gold layers using dbt, and serves
results via a live API and dashboard.

**Live demo:** [DASHBOARD_URL] | **API:** https://de-pipeline-w3km.vercel.app/

![dashboard screenshot](./docs/screenshot.png)

## Stack
Python · Postgres (Neon) · dbt · GitHub Actions · FastAPI (Vercel) · React (Vercel)

## Architecture
[diagram — see Part 1]

## What this demonstrates
- Idempotent, tested ingestion with retry logic
- dbt-managed transformations with automated data quality tests (not_null, unique)
- Bad-data filtering with visible rejection counts in every dbt run
- Fully managed, serverless infra — zero servers to maintain, no billing card needed, scales automatically
- Pipeline observability via /api/pipeline-health endpoint and pipeline_logs table

## About the dataset
The ridership data (Citi Bike, 443K+ rows) covers December 2013. Weather data
for that same period was backfilled from Open-Meteo's historical archive API
to match. The pipeline itself runs live every day via GitHub Actions —
ingestion, dbt transforms, and tests all execute on schedule — but since the
underlying ridership source is a fixed historical export, `gold_daily_summary`
reflects December 2013 rather than the current date. This setup was chosen to
demonstrate full pipeline automation and orchestration against a real,
substantial dataset, rather than a live-updating dashboard.

## Known limitations
- Ridership CSV must be manually refreshed periodically (no stable free API for this data source)
- Free-tier limits apply on Neon/Vercel — sufficient for this project's scale
- Serverless cold starts mean the first API request after idle time may take ~1-2s longer

## How to run locally
[setup steps from Part 3]