

SELECT
    source_date AS date,
    (raw_json->'daily'->'temperature_2m_mean'->>0)::float AS temp_avg_c,
    (raw_json->'daily'->'precipitation_sum'->>0)::float AS precipitation_mm,
    (raw_json->'daily'->'windspeed_10m_max'->>0)::float AS wind_speed_kmh
FROM "neondb"."public"."bronze_weather"
WHERE raw_json->'daily'->'temperature_2m_mean'->>0 IS NOT NULL