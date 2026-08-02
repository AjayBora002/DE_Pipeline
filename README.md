# Weather–Ridership Data Pipeline

Automated batch pipeline: ingests weather + ridership data daily, validates
and transforms it through bronze/silver/gold layers using dbt, and serves
results via a live API and dashboard.

Open-Meteo API ──┐
                  ├──► bronze_weather / bronze_ridership (raw, untouched)
Citi Bike CSV ────┘         │
                             ▼ dbt (SQL transforms)
                    silver_weather / silver_ridership (cleaned, typed, filtered)
                             │
                             ▼ dbt (join + aggregate)
                      gold_daily_summary (one row per day)
                             │
                             ▼
                    FastAPI (api/index.py) ──► React dashboard

   <img width="656" height="634" alt="{8C7316F1-5BD5-41DC-B77C-4486B3951A16}" src="https://github.com/user-attachments/assets/15b985b3-bf1a-4e60-b303-a7ff0b74ff03" />

<img width="1837" height="921" alt="scrren" src="https://github.com/user-attachments/assets/482e27ad-0b3e-4bd6-b751-4d8e34ed2b9d" />


                    
**Live demo:** [DASHBOARD_URL] | **API:** https://de-pipeline-w3km.vercel.app/


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
## Challenges & Solutions

Building this surfaced a few real production-style problems worth documenting:

**Zero rows in the final table.** The gold layer joins ridership and weather
on date, but returned zero rows no matter how the SQL was written. Root
cause: the ridership CSV is a fixed December 2013 export, while the weather
ingestion only ever pulled "today's" data — so the two tables never shared
a single overlapping date. Fixed by writing a one-time backfill script
using Open-Meteo's historical archive API to populate matching 2013 weather.

**A 6-hour pipeline run.** The initial ridership loader inserted 443K rows
either unbatched or one at a time. Rewrote it to batch inserts in chunks of
5,000 using `execute_values`, committing after each batch — brought total
runtime down to under 2 minutes.

**An undocumented Vercel routing change.** The deployed API returned 404 on
every route, including its own auto-generated docs page — despite building
successfully. The build log's warning line revealed the real cause: Vercel
now routes backend-framework projects using the rewrite's *destination*
path rather than the actual requested URL, so every request looked
identical to the app internally. Fixed by dropping the custom rewrite and
adopting Vercel's native `api/` directory convention instead.

**A stray newline breaking a database connection.** A GitHub Actions secret
update silently introduced a trailing newline into the connection string
via browser copy-paste, causing `invalid sslmode value: "require\n"`. Fixed
by setting the secret through the GitHub CLI instead of the web UI, which
avoids clipboard-introduced whitespace entirely.
## How to run locally
[setup steps from Part 3]
