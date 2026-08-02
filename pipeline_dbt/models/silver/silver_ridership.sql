{{ config(materialized='table') }}

WITH parsed AS (
    SELECT
        md5((raw_row->>'starttime') || (raw_row->>'bikeid')) AS trip_id,
        (raw_row->>'starttime')::timestamp AS started_at,
        (raw_row->>'stoptime')::timestamp AS ended_at,
        COALESCE(raw_row->>'start station name', 'unknown') AS station_start,
        COALESCE(raw_row->>'end station name', 'unknown') AS station_end
    FROM {{ source('bronze', 'bronze_ridership') }}
    WHERE raw_row->>'starttime' IS NOT NULL
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