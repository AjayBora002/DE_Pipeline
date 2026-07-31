

SELECT
    r.start_date AS date,
    COUNT(*) AS total_rides,
    AVG(r.duration_minutes) AS avg_trip_duration_min,
    w.temp_avg_c,
    w.precipitation_mm,
    AVG(COUNT(*)) OVER (ORDER BY r.start_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rides_7day_rolling_avg
FROM "neondb"."public_public"."silver_ridership" r
JOIN "neondb"."public_public"."silver_weather" w ON r.start_date = w.date
GROUP BY r.start_date, w.temp_avg_c, w.precipitation_mm