{{ config(materialized='table') }}

WITH parsed AS (
    SELECT
        raw_row->>'ride_id' AS trip_id,
        (raw_row->>'started_at')::timestamp AS started_at,
        (raw_row->>'ended_at')::timestamp AS ended_at,
        COALESCE(raw_row->>'start_station_name', 'unknown') AS station_start,
        COALESCE(raw_row->>'end_station_name', 'unknown') AS station_end
    FROM {{ source('bronze', 'bronze_ridership') }}
    WHERE raw_row->>'ride_id' IS NOT NULL
),
calculated AS (
    SELECT
        trip_id,
        started_at::date AS start_date,
        EXTRACT(EPOCH FROM (ended_at - started_at)) / 60 AS duration_minutes,
        station_start,
        station_end
    FROM parsed
)
SELECT *
FROM calculated
WHERE duration_minutes > 0 AND duration_minutes <= 1440