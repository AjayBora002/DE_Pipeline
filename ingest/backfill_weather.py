import os
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
LAT, LON = 29.22, 79.53

START_DATE = "2013-12-01"
END_DATE = "2013-12-31"

def fetch_historical_weather(start_date, end_date):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_mean,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def save_daily_rows(data):
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cur = conn.cursor()

    dates = data["daily"]["time"]
    temps = data["daily"]["temperature_2m_mean"]
    precip = data["daily"]["precipitation_sum"]
    wind = data["daily"]["windspeed_10m_max"]

    for i, date_str in enumerate(dates):
        # build a per-day payload matching the same shape your existing
        # silver_weather.sql model already expects (daily.*[0])
        daily_payload = {
            "daily": {
                "temperature_2m_mean": [temps[i]],
                "precipitation_sum": [precip[i]],
                "windspeed_10m_max": [wind[i]],
            }
        }
        cur.execute(
            """
            INSERT INTO bronze_weather (source_date, raw_json)
            VALUES (%s, %s)
            ON CONFLICT (source_date) DO UPDATE SET raw_json = EXCLUDED.raw_json
            """,
            (date_str, Json(daily_payload)),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Backfilled {len(dates)} days of historical weather ({START_DATE} to {END_DATE}).")

if __name__ == "__main__":
    data = fetch_historical_weather(START_DATE, END_DATE)
    save_daily_rows(data)