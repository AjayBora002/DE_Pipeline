import os
import time
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import date
from utils.logger import log_run

DATABASE_URL = os.environ["DATABASE_URL"]
LAT, LON = 29.22, 79.53

def fetch_with_retry(fn, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"Attempt {attempt+1} failed: {e}, retrying in {delay}s...")
            time.sleep(delay)

def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&daily=temperature_2m_mean,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto&past_days=1&forecast_days=1"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def save_to_bronze(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bronze_weather (source_date, raw_json)
        VALUES (%s, %s)
        ON CONFLICT (source_date) DO UPDATE SET raw_json = EXCLUDED.raw_json
        """,
        (date.today(), Json(data)),
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        data = fetch_with_retry(fetch_weather)
        save_to_bronze(data)
        log_run("weather_ingest", "success")
        print("Weather ingestion successful.")
    except Exception as e:
        log_run("weather_ingest", "failed", str(e))
        print(f"Weather ingestion FAILED: {e}")
        raise