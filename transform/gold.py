import os
import psycopg2
from utils.logger import log_run


DATABASE_URL = os.environ["DATABASE_URL"]

GOLD_QUERY = """
INSERT INTO gold_daily_summary (date, total_rides, avg_trip_duartion_min, temp_avg_c, precipitation_mm, rides_7day_rolling_avg)
SELECT
  r.start_date AS date,
  COUNT(*) AS total_rides,
  AVG(r.duration_minutes) AS avg_trip_duration_min,
    w.temp_avg_c,
    w.precipitation_mm,
    AVG(COUNT(*)) OVER (ORDER BY r.start_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rides_7day_rolling_avg
FROM silver_ridership r
JOIN silver_weather w ON r.start_date = w.date
GROUP BY r.start_date, w.temp_avg_c, w.precipitation_mm
ON CONFLICT (date) DO UPDATE SET
    total_rides = EXCLUDED.total_rides,
    avg_trip_duration_min = EXCLUDED.avg_trip_duration_min,
    temp_avg_c = EXCLUDED.temp_avg_c,
    precipitation_mm = EXCLUDED.precipitation_mm,
    rides_7day_rolling_avg = EXCLUDED.rides_7day_rolling_avg;
"""

if __name__ == "__main__":
  try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(GOLD_QUERY)
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    log_run("gold_aggregation", "success", f"{affected} rows")
    print(f"Gold layer updated: {affected} rows affected.")
  except Exception as e:
    log_run("gold_aggregation", "failed", str(e))
    print(f"Gold aggregation FAILED: {e}")
    raise