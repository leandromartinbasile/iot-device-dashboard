import { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

const API_BASE = "http://localhost:8000/api";
const DEVICE_ID = 1;

function App() {
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReadings = async () => {
      try {
        const res = await axios.get(
          `${API_BASE}/devices/${DEVICE_ID}/readings/`,
          { withCredentials: true }
        );
        const sorted = [...res.data.readings].reverse();
        setReadings(sorted);
        setError(null);
      } catch (err) {
        setError("Could not load readings. Are you logged into Django admin?");
      }
    };

    fetchReadings();
    const interval = setInterval(fetchReadings, 5000);
    return () => clearInterval(interval);
  }, []);

  // Reshape: one row per timestamp, one column per metric
  const chartDataByTime = {};
  readings.forEach((r) => {
    const time = new Date(r.timestamp).toLocaleTimeString();
    if (!chartDataByTime[time]) {
      chartDataByTime[time] = { time };
    }
    chartDataByTime[time][r.metric] = r.value;
  });
  const chartData = Object.values(chartDataByTime);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Device Dashboard</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>Temperature</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="temperature" stroke="#e07a5f" connectNulls />
        </LineChart>
      </ResponsiveContainer>

      <h2>Humidity</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="humidity" stroke="#3d5a80" connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default App;
