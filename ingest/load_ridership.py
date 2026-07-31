import os
import csv
import psycopg2
from psycopg2.extras import Json
from utils.logger import log_run


DATABASE_URL = os.environ["DATABASE_URL"]
CSV_PATH = "data/sample_trips.csv"

def load_csv_to_bronze():
  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor()

  cur.execute(
    "SELECT COUNT(*) FROM bronze_ridership where source_file = %s",
    (CSV_PATH,),
  )
  if cur.fetchone()[0] >0:
    print(f"{CSV_PATH} already loaded, skipping.")
    cur.close()
    conn.close()
    return


  with open (CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [dict(row) for row in reader]


  for row in rows:
    cur.execute(
      "INSERT INTO bronze_ridership (source_file, raw_row) VALUES(%s, %s)",
      (CSV_PATH, Json(row)),
    )

  conn.commit()
  cur.close()
  conn.close()
  print(f"Loaded {len(rows)} rows from {CSV_PATH}")


if __name__ == "__main__":
  try:
    load_csv_to_bronze()
    log_run("ridership_ingest", "success")
  except Exception as e:
    log_run("ridership_ingest", "failed", str(e))
    print(f"Ridership ingestion FAILED: {e}")
    raise