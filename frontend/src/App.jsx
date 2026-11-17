import { useState, useEffect, useCallback } from "react";
import {
  Wind,
  LayoutDashboard,
  Activity,
  History,
  Thermometer,
  Droplets,
  Users,
  RefreshCw,
  Settings,
  Brain,
  Zap,
  Power,
  CheckCircle,
  AlertCircle,
  Clock,
  Trash2,
  Gauge,
  Sparkles,
} from "lucide-react";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";

import Fan3D from "./components/Fan3D";
import { getPrediction, checkHealth } from "./services/api";
import "./index.css";

const INITIAL_INPUT = {
  temperature: 28,
  humidity: 55,
  occupied: true,
  comfort_preference: "Balanced",
  manual_override: false,
  manual_speed: "Medium",
};

const SPEEDS = ["Off", "Low", "Medium", "High"];

const SPEED_COLORS = {
  Off: "#9ca3af",
  Low: "#60a5fa",
  Medium: "#dba520",
  High: "#22c55e",
};

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem("airmind_history") || "[]");
  } catch {
    return [];
  }
}

function StatCard({ title, value, unit, icon: Icon, color }) {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <span>{title}</span>
        <Icon size={19} color={color} />
      </div>
      <div className="stat-value">
        {value}
        {unit && <span className="stat-unit">{unit}</span>}
      </div>
    </div>
  );
}

function SectionTitle({ icon: Icon, title, subtitle }) {
  return (
    <div className="section-title">
      <div className="section-icon">
        <Icon size={18} />
      </div>
      <div>
        <h3>{title}</h3>
        {subtitle && <p>{subtitle}</p>}
      </div>
    </div>
  );
}

function SpeedBadge({ speed }) {
  return (
    <span
      className="speed-badge"
      style={{
        color: SPEED_COLORS[speed] || "#64748b",
        background: `${SPEED_COLORS[speed] || "#64748b"}18`,
      }}
    >
      <span
        className="speed-dot"
        style={{ background: SPEED_COLORS[speed] }}
      />
      {speed}
    </span>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [input, setInput] = useState(INITIAL_INPUT);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState(getHistory);

  const runPrediction = useCallback(async (currentInput = input) => {
    setLoading(true);
    setError("");

    try {
      const result = await getPrediction(currentInput);

      setPrediction(result);

      const entry = {
        ...result,
        timestamp: new Date().toISOString(),
      };

      setHistory((previous) => {
        const updated = [entry, ...previous].slice(0, 50);
        localStorage.setItem("airmind_history", JSON.stringify(updated));
        return updated;
      });

      setBackendOnline(true);
    } catch (err) {
      setBackendOnline(false);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Unable to connect to backend"
      );
    } finally {
      setLoading(false);
    }
  }, [input]);

  const refreshHealth = async () => {
    try {
      const health = await checkHealth();
      setBackendOnline(health.status === "online" && health.model_loaded);
    } catch {
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    refreshHealth();
    runPrediction(INITIAL_INPUT);
  }, []);

  const updateInput = (key, value) => {
    setInput((previous) => ({
      ...previous,
      [key]: value,
    }));
  };

  const handleManualSpeed = (speed) => {
    const updated = {
      ...input,
      manual_override: true,
      manual_speed: speed,
    };

    setInput(updated);
    runPrediction(updated);
  };

  const enableAutomaticMode = () => {
    const updated = {
      ...input,
      manual_override: false,
    };

    setInput(updated);
    runPrediction(updated);
  };

  const clearHistory = () => {
    localStorage.removeItem("airmind_history");
    setHistory([]);
  };

  const fanSpeed = prediction?.final_recommendation || "Off";

  const chartHistory = [...history]
    .slice(0, 12)
    .reverse()
    .map((item, index) => ({
      name: index + 1,
      temperature: item.temperature,
      humidity: item.humidity,
    }));

  const speedDistribution = SPEEDS.map((speed) => ({
    speed,
    count: history.filter(
      (item) => item.final_recommendation === speed
    ).length,
  }));

  const navigation = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "Analytics", icon: Activity },
    { name: "History", icon: History },
  ];

  return (
    <div className="airmind-app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">
            <Wind size={25} />
          </div>
          <div>
            <h2>AirMind AI</h2>
            <p>Intelligent Comfort</p>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${
                activePage === name ? "active" : ""
              }`}
              onClick={() => setActivePage(name)}
            >
              <Icon size={18} />
              <span>{name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span
              className={`status-dot ${
                backendOnline ? "online" : "offline"
              }`}
            />
            <span>{backendOnline ? "System Online" : "System Offline"}</span>
          </div>

          <div className="sidebar-footer">
            <Wind size={15} />
            Air, Engineered to Think.
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-content">
        <header className="page-header">
          <div>
            <h1>{activePage}</h1>
            <p>Context-aware intelligent comfort system</p>
          </div>

          <div className="header-actions">
            <div className="connection-badge">
              {backendOnline ? (
                <CheckCircle size={15} color="#16a34a" />
              ) : (
                <AlertCircle size={15} color="#dc2626" />
              )}
              {backendOnline ? "Backend Connected" : "Backend Offline"}
            </div>

            <button
              className="refresh-button"
              onClick={() => runPrediction()}
              disabled={loading}
              title="Refresh prediction"
            >
              <RefreshCw
                size={18}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </header>

        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* OVERVIEW */}
        {activePage === "Overview" && (
          <>
            <div className="stats-grid">
              <StatCard
                title="Temperature"
                value={input.temperature}
                unit="°C"
                icon={Thermometer}
                color="#f97316"
              />

              <StatCard
                title="Humidity"
                value={input.humidity}
                unit="%"
                icon={Droplets}
                color="#3b82f6"
              />

              <StatCard
                title="Occupancy"
                value={input.occupied ? "Occupied" : "Empty"}
                icon={Users}
                color="#8b5cf6"
              />

              <StatCard
                title="Fan Recommendation"
                value={fanSpeed}
                icon={Wind}
                color="#16a34a"
              />
            </div>

            <div className="overview-layout">
              {/* FAN */}
              <section className="panel fan-panel">
                <div className="panel-header">
                  <div>
                    <h3>Live Fan Simulation</h3>
                    <p>3D animation responds to AI recommendation</p>
                  </div>

                  <SpeedBadge speed={fanSpeed} />
                </div>

                <Fan3D speed={fanSpeed} />

                <div className="control-mode-card">
                  <div>
                    <span>Control Mode</span>
                    <strong>
                      {prediction?.control_mode || "Waiting for prediction"}
                    </strong>
                  </div>
                  <Power
                    size={19}
                    color={
                      fanSpeed === "Off" ? "#9ca3af" : "#16a34a"
                    }
                  />
                </div>
              </section>

              {/* ENVIRONMENT */}
              <section className="panel environment-panel">
                <SectionTitle
                  icon={Settings}
                  title="Environment"
                />

                <div className="input-group">
                  <div className="input-label">
                    <label>Temperature</label>
                    <strong>{input.temperature}°C</strong>
                  </div>

                  <input
                    type="range"
                    min="18"
                    max="40"
                    value={input.temperature}
                    onChange={(e) =>
                      updateInput("temperature", Number(e.target.value))
                    }
                  />
                </div>

                <div className="input-group">
                  <div className="input-label">
                    <label>Humidity</label>
                    <strong>{input.humidity}%</strong>
                  </div>

                  <input
                    type="range"
                    min="20"
                    max="95"
                    value={input.humidity}
                    onChange={(e) =>
                      updateInput("humidity", Number(e.target.value))
                    }
                  />
                </div>

                <div className="input-group">
                  <label>Comfort Preference</label>

                  <select
                    value={input.comfort_preference}
                    onChange={(e) =>
                      updateInput("comfort_preference", e.target.value)
                    }
                  >
                    <option>Energy-conscious</option>
                    <option>Balanced</option>
                    <option>More airflow</option>
                  </select>
                </div>

                <label className="occupancy-toggle">
                  <input
                    type="checkbox"
                    checked={input.occupied}
                    onChange={(e) =>
                      updateInput("occupied", e.target.checked)
                    }
                  />
                  <span>Room Occupied</span>
                </label>

                <div className="manual-section">
                  <label>Manual Override</label>

                  <div className="speed-buttons">
                    {SPEEDS.map((speed) => (
                      <button
                        key={speed}
                        className={
                          input.manual_override &&
                          input.manual_speed === speed
                            ? "selected"
                            : ""
                        }
                        onClick={() => handleManualSpeed(speed)}
                      >
                        {speed}
                      </button>
                    ))}
                  </div>

                  <button
                    className="automatic-button"
                    onClick={enableAutomaticMode}
                  >
                    Automatic Mode
                  </button>
                </div>

                <button
                  className="predict-button"
                  onClick={() => runPrediction()}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={16} className="spin" />
                      Predicting...
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} />
                      Apply & Predict
                    </>
                  )}
                </button>
              </section>
            </div>

            {/* EXPLANATION + SCORES */}
            <div className="bottom-grid">
              <section className="panel">
                <SectionTitle
                  icon={Brain}
                  title="AI Decision Explanation"
                  subtitle="Why the system selected this fan speed"
                />

                <div className="explanation-list">
                  {prediction?.explanation?.length ? (
                    prediction.explanation.map((item, index) => (
                      <div className="explanation-item" key={index}>
                        <span className="explanation-bullet" />
                        <p>{item}</p>
                      </div>
                    ))
                  ) : (
                    <p className="muted">
                      Run a prediction to view the explanation.
                    </p>
                  )}
                </div>
              </section>

              <section className="panel">
                <SectionTitle
                  icon={Gauge}
                  title="Model Scores"
                  subtitle="Random Forest class probabilities"
                />

                <div className="score-list">
                  {Object.entries(prediction?.model_scores || {}).map(
                    ([label, score]) => (
                      <div className="score-item" key={label}>
                        <div className="score-header">
                          <span>{label}</span>
                          <strong>{score}%</strong>
                        </div>

                        <div className="score-track">
                          <div
                            className="score-fill"
                            style={{
                              width: `${score}%`,
                              background: SPEED_COLORS[label],
                            }}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>
              </section>
            </div>

            {/* SHAP */}
            <section className="panel shap-panel">
              <SectionTitle
                icon={Brain}
                title="SHAP Feature Contributions"
                subtitle="Feature contribution to the predicted ML class"
              />

              {prediction?.shap_explanation?.length ? (
                <ResponsiveContainer width="100%" height={230}>
                  <BarChart
                    data={prediction.shap_explanation}
                    layout="vertical"
                    margin={{ left: 25, right: 25 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee6da" />
                    <XAxis type="number" />
                    <YAxis
                      type="category"
                      dataKey="feature"
                      width={145}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="impact"
                      fill="#dba520"
                      radius={[0, 5, 5, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="muted">
                  SHAP explanation will appear after a successful prediction.
                </p>
              )}
            </section>
          </>
        )}

        {/* ANALYTICS */}
        {activePage === "Analytics" && (
          <div className="analytics-grid">
            <section className="panel chart-panel">
              <SectionTitle
                icon={Activity}
                title="Environmental Trends"
                subtitle="Recent prediction history"
              />

              {chartHistory.length ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee6da" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="temperature"
                      stroke="#f97316"
                      strokeWidth={3}
                    />
                    <Line
                      type="monotone"
                      dataKey="humidity"
                      stroke="#3b82f6"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="muted">No prediction history available.</p>
              )}
            </section>

            <section className="panel chart-panel">
              <SectionTitle
                icon={Wind}
                title="Fan Recommendation Distribution"
                subtitle="Recommendations in local history"
              />

              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={speedDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eee6da" />
                  <XAxis dataKey="speed" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#dba520" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </section>
          </div>
        )}

        {/* HISTORY */}
        {activePage === "History" && (
          <section className="panel history-panel">
            <div className="panel-header">
              <SectionTitle
                icon={History}
                title="Prediction History"
                subtitle={`${history.length} recorded predictions`}
              />

              <button
                className="clear-history-button"
                onClick={clearHistory}
              >
                <Trash2 size={15} />
                Clear History
              </button>
            </div>

            {history.length ? (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Temperature</th>
                      <th>Humidity</th>
                      <th>Occupancy</th>
                      <th>Recommendation</th>
                      <th>Control Mode</th>
                    </tr>
                  </thead>

                  <tbody>
                    {history.map((item, index) => (
                      <tr key={`${item.timestamp}-${index}`}>
                        <td>
                          {item.timestamp
                            ? new Date(item.timestamp).toLocaleString()
                            : "—"}
                        </td>
                        <td>{item.temperature}°C</td>
                        <td>{item.humidity}%</td>
                        <td>{item.occupied ? "Occupied" : "Empty"}</td>
                        <td>
                          <SpeedBadge speed={item.final_recommendation} />
                        </td>
                        <td>{item.control_mode}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-history">
                <Clock size={30} />
                <h3>No history yet</h3>
                <p>Run predictions to build your history.</p>
              </div>
            )}
          </section>
        )}

        <footer className="app-footer">
          <span>AirMind AI</span>
          <span>Intelligent Comfort System · Prototype</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
