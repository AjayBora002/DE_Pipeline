import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app =FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_methods = ["*"],
  allow_headers= ["*"],

)

DATABASE_URL = os.environ["DATABASE_URL"]


@app.get("/api/daily-summary")
def get_summary():
  conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
  cur = conn.cursor(cursor_factory = RealDictCursor)
  cur.execute("SELECT * FROM gold_daily_summary ORDER BY date DESC LIMIT 60")
  rows = cur.fetchall()
  cur.close()
  conn.close()
  return rows

@app.get("/api/pipeline-health")
def pipeline_health():
  conn = psycopg2.connect(DATABASE_URL)
  cur = conn.cursor(cursor_factory = RealDictCursor)
  cur.execute("SELECT * FROM pipeline_logs ORDER BY run_at DESC LIMIT 10")
  rows = cur.fetchall()
  cur.close()
  conn.close()
  return rows

@app.get("/api/health")
def health():
  return {"status": "ok"}