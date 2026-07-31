import os
import psycopg2

DATABASE_URL = os.environ["DATABASE_URL"]

def log_run(step, status, message=""):
  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor()
  cur.execute(
    "INSERT INTO pipeline_logs (step, status, message) values (%s, %s, %s)",
    (step, status, message),
  )
  conn.commit()
  cur.close()
  conn.close()

