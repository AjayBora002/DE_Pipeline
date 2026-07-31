import os
import psycopg2
from psycopg2.extras import RealDictCursor
from utils.logger import log_run

DATABASE_URL = os.environ["DATABASE_URL"]


def transform_weather():
  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor(cursor_factory = RealDictCursor)
  cur.execute(
    "SELECT source_date, raw_json from bronze_weather"  
  )
  rows = cur.fetchall()

  write_cur = conn.cursor()
  processed, skipped = 0, 0
  for row in rows:
    daily = row["raw_json"].get("daily",{})
    try:
      temp = daily["temperature_2m_mean"][0]
      precip = daily["precipitation_sum"][0]
      wind = daily["windspeed_10m_max"][0]
    except(KeyError, IndexError):
      skipped +=1
      continue

    write_cur.execute(
      """INSERT INTO silver_weather (date, temp_avg_c, precipitation_mm, wind_speed_kmp)
      VALUES (%s, %s, %s, %s)
      ON CONFLICT (date) DO UPDATE SET
        temp_avg_c = EXCLUDED.temp_avg_c,
        precipitation_mm = EXCLUDED.precipitation_mm,
        wind_speed_kmh = EXCLUDED.wind_speed_kmh
      """,
      (row["source_date"],temp, precip, wind),
    )
    processed+=1
  conn.commit()
  cur.close()
  write_cur.close()
  conn.close()
  print(f"Silver weather: {processed} processed, {skipped} skipped.")

def transform_ridership():
  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor(cursor_factory = RealDictCursor)
  cur.execute("SELECT raw_row FROM bronze_ridership")
  rows = cur.fetchall()

  write_cur = conn.cursor()
  processed, skipped = 0, 0
  for row in rows:
    r = row["raw_row"]
    try:
      trip_id= r["ride_id"]
      start_date = r["started_at"][:10]
      start_time= r["started_at"]
      end_time = r["ebded_at"]
      station_start = r.get("station_start_name", "unknown")
      station_end = r.get("end_station_name", "unknown")


      from datetime import datetime
      fmt = "%Y-%m-%d %H:%M:%S"
      duration =(
        datetime.formisoformat(end_time) - datetime.fromisoformat(start_time)   
      ).total_seconds() / 60


      if duration <= 0 or duration > 1440:
        skipped+=1
        continue

    except(KeyError, ValueError, TypeError):
      skipped+=1
      continue

    write_cur.execute(
      """
      INSERT INTO silver_ridership (trip_id, start_date, duration_minutes, station_start, station_end)
      VALUES (%s, %s, %s, %s, %s)
      ON CONFLICT (trip_id) DO UPDATE SET
          duration_minutes = EXCLUDED.duration_minutes
      """,
      (trip_id, start_date, duration, station_start, station_end),
    )
    processed += 1
  conn.commit()
  cur.close()
  write_cur.close()
  conn.close()
  print(f"Silver ridership: {processed} processed, {skipped} skipped.")


if __name__ == "__main__":
  try:
    transform_weather()
    transform_ridership()
    log_run("silver_transform", "success")
  except Exception as e:
    log_run("silver_transform", "failed", str(e))
    print(f"Silver transform FAILED: {e}")
    raise