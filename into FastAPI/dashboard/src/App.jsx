import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

const API_URL = "https://your-app.onrender.com/daily-summary"; // replace with your real Render URL

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(API_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        return res.json();
      })
      .then((rows) => {
        // reverse so chart reads oldest -> newest, left to right
        setData(rows.slice().reverse());
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={styles.centered}>Loading pipeline data...</div>;
  }

  if (error) {
    return (
      <div style={styles.centered}>
        Failed to load data: {error}
        <br />
        Check that the API URL is correct and the Render service is running.
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Ridership vs Weather</h1>
        <p style={styles.subtitle}>
          Daily bike ridership compared against weather conditions, updated automatically each day.
        </p>
      </header>

      <section style={styles.chartCard}>
        <h2 style={styles.sectionTitle}>Ridership Trend (7-day rolling average)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total_rides" stroke="#2563eb" name="Total Rides" />
            <Line type="monotone" dataKey="rides_7day_rolling_avg" stroke="#16a34a" name="7-day Avg" />
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section style={styles.tableCard}>
        <h2 style={styles.sectionTitle}>Daily Summary</h2>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Date</th>
              <th style={styles.th}>Total Rides</th>
              <th style={styles.th}>Avg Trip (min)</th>
              <th style={styles.th}>Avg Temp (°C)</th>
              <th style={styles.th}>Precipitation (mm)</th>
              <th style={styles.th}>7-day Avg</th>
            </tr>
          </thead>
          <tbody>
            {data.slice().reverse().map((row) => (
              <tr key={row.date}>
                <td style={styles.td}>{row.date}</td>
                <td style={styles.td}>{row.total_rides}</td>
                <td style={styles.td}>{row.avg_trip_duration_min?.toFixed(1)}</td>
                <td style={styles.td}>{row.temp_avg_c?.toFixed(1)}</td>
                <td style={styles.td}>{row.precipitation_mm?.toFixed(1)}</td>
                <td style={styles.td}>{row.rides_7day_rolling_avg?.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer style={styles.footer}>
        Data updates daily via an automated pipeline (GitHub Actions → Postgres → FastAPI).
      </footer>
    </div>
  );
}

const styles = {
  page: {
    fontFamily: "system-ui, sans-serif",
    maxWidth: "900px",
    margin: "0 auto",
    padding: "2rem 1rem",
    color: "#1e293b",
  },
  centered: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    fontFamily: "system-ui, sans-serif",
    textAlign: "center",
    padding: "1rem",
  },
  header: { marginBottom: "2rem" },
  title: { fontSize: "1.8rem", marginBottom: "0.25rem" },
  subtitle: { color: "#64748b", fontSize: "0.95rem" },
  chartCard: {
    background: "#f8fafc",
    borderRadius: "8px",
    padding: "1.5rem",
    marginBottom: "2rem",
  },
  tableCard: {
    background: "#f8fafc",
    borderRadius: "8px",
    padding: "1.5rem",
    overflowX: "auto",
  },
  sectionTitle: { fontSize: "1.1rem", marginBottom: "1rem" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" },
  th: {
    textAlign: "left",
    padding: "0.5rem",
    borderBottom: "2px solid #cbd5e1",
  },
  td: {
    padding: "0.5rem",
    borderBottom: "1px solid #e2e8f0",
  },
  footer: {
    marginTop: "2rem",
    textAlign: "center",
    color: "#94a3b8",
    fontSize: "0.85rem",
  },
};