import {
  Activity,
  AlertCircle,
  BarChart3,
  Gauge,
  Globe2,
  LineChart,
  Loader2,
  Play,
  RefreshCcw,
  ShieldAlert,
  Target
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ReferenceDot,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import {
  analyzeRisk,
  fetchFrontier,
  health,
  optimizePortfolio,
  runMonteCarlo
} from "./api/quantApi.js";

const COLORS = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#7c3aed", "#0891b2"];

const OPTIMIZER_OPTIONS = [
  { value: "scipy_max_sharpe", label: "SciPy Max Sharpe" },
  { value: "random_search", label: "Random Search" }
];

const MARKET_PRESETS = {
  us: {
    label: "US Market",
    tickers: "AAPL, MSFT, GOOGL, AMZN",
    benchmark: "SPY",
    riskFreeRate: 0.04,
    initialValue: 100000,
    currency: "USD"
  },
  india: {
    label: "Indian Market",
    tickers: "RELIANCE, TCS, INFY, HDFCBANK",
    benchmark: "^NSEI",
    riskFreeRate: 0.065,
    initialValue: 1000000,
    currency: "INR"
  }
};

const initialForm = {
  market: "us",
  optimizer: "scipy_max_sharpe",
  tickers: "AAPL, MSFT, GOOGL, AMZN",
  start: "2023-01-01",
  end: "2026-01-01",
  benchmark: "SPY",
  riskFreeRate: 0.04,
  maxWeight: 0.6,
  trials: 12000,
  frontierPoints: 8,
  monteCarloDays: 252,
  monteCarloSimulations: 600,
  initialValue: 100000
};

function parseTickers(value) {
  return value
    .split(",")
    .map((ticker) => ticker.trim().toUpperCase())
    .filter(Boolean);
}

function formatPercent(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return `${(value * 100).toFixed(digits)}%`;
}

function formatCurrency(value, currency = "USD") {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return new Intl.NumberFormat(currency === "INR" ? "en-IN" : "en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0
  }).format(value);
}

function formatCompactCurrency(value, currency = "USD") {
  const symbol = currency === "INR" ? "₹" : "$";
  return `${symbol}${Math.round(value / 1000)}k`;
}

function toAllocationData(weights = {}) {
  return Object.entries(weights)
    .map(([ticker, weight]) => ({ ticker, weight }))
    .sort((a, b) => b.weight - a.weight);
}

function toFrontierData(points = []) {
  return points.map((point) => ({
    ...point,
    volatilityPct: point.volatility * 100,
    returnPct: point.expected_return * 100,
    sharpe: point.sharpe_ratio
  }));
}

function toMonteCarloData(simulation) {
  if (!simulation?.p50) return [];
  return simulation.p50.map((value, index) => ({
    day: index + 1,
    p10: simulation.p10[index],
    p25: simulation.p25[index],
    p50: value,
    p75: simulation.p75[index],
    p90: simulation.p90[index]
  }));
}

export function App() {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState({ backend: "checking", quantEngine: "checking" });
  const [optimization, setOptimization] = useState(null);
  const [risk, setRisk] = useState(null);
  const [frontier, setFrontier] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    health()
      .then((payload) => {
        setStatus({
          backend: payload.backend,
          quantEngine: payload.quantEngine?.status ?? "unknown"
        });
      })
      .catch(() => {
        setStatus({ backend: "offline", quantEngine: "offline" });
      });
  }, []);

  const allocationData = useMemo(() => toAllocationData(optimization?.weights), [optimization]);
  const frontierData = useMemo(() => toFrontierData(frontier?.points), [frontier]);
  const simulationData = useMemo(() => toMonteCarloData(simulation), [simulation]);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function selectMarket(market) {
    const preset = MARKET_PRESETS[market];
    setForm((current) => ({
      ...current,
      market,
      tickers: preset.tickers,
      benchmark: preset.benchmark,
      riskFreeRate: preset.riskFreeRate,
      initialValue: preset.initialValue
    }));
  }

  async function runAnalysis() {
    const tickers = parseTickers(form.tickers);
    if (tickers.length < 2) {
      setError("Enter at least two tickers.");
      return;
    }

    setLoading(true);
    setError("");
    setOptimization(null);
    setRisk(null);
    setFrontier(null);
    setSimulation(null);

    try {
      const marketBase = {
        market: form.market,
        tickers,
        start: form.start,
        end: form.end || null
      };

      const optimized = await optimizePortfolio({
        ...marketBase,
        optimizer: form.optimizer,
        riskFreeRate: Number(form.riskFreeRate),
        maxWeight: Number(form.maxWeight),
        trials: Number(form.trials),
        seed: 42
      });
      setOptimization(optimized);

      const [riskPayload, frontierPayload, monteCarloPayload] = await Promise.all([
        analyzeRisk({
          ...marketBase,
          weights: optimized.weights,
          benchmark: form.benchmark || null,
          confidence: 0.95
        }),
        fetchFrontier({
          ...marketBase,
          riskFreeRate: Number(form.riskFreeRate),
          maxWeight: Number(form.maxWeight),
          points: Number(form.frontierPoints),
          trials: Math.max(2000, Math.floor(Number(form.trials) / 2)),
          seed: 42
        }),
        runMonteCarlo({
          ...marketBase,
          weights: optimized.weights,
          days: Number(form.monteCarloDays),
          simulations: Number(form.monteCarloSimulations),
          initialValue: Number(form.initialValue),
          seed: 42
        })
      ]);

      setRisk(riskPayload);
      setFrontier(frontierPayload);
      setSimulation(monteCarloPayload);
    } catch (exception) {
      setError(exception.message);
    } finally {
      setLoading(false);
    }
  }

  const optimalPoint = optimization
    ? {
        volatilityPct: optimization.volatility * 100,
        returnPct: optimization.expected_return * 100
      }
    : null;

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="control-panel">
          <div className="brand-row">
            <div className="mark">
              <Activity size={22} />
            </div>
            <div>
              <h1>Quant Optimizer</h1>
              <p>Java API + Python engine</p>
            </div>
          </div>

          <div className="service-strip" aria-label="Service status">
            <span className={status.backend === "ok" ? "dot ok" : "dot bad"} />
            <span>Backend {status.backend}</span>
            <span className={status.quantEngine === "ok" ? "dot ok" : "dot bad"} />
            <span>Engine {status.quantEngine}</span>
          </div>

          <div className="market-tabs" role="tablist" aria-label="Market selection">
            {Object.entries(MARKET_PRESETS).map(([market, preset]) => (
              <button
                key={market}
                className={form.market === market ? "market-tab active" : "market-tab"}
                type="button"
                role="tab"
                aria-selected={form.market === market}
                onClick={() => selectMarket(market)}
              >
                <Globe2 size={16} />
                <span>{preset.label}</span>
              </button>
            ))}
          </div>

          <label className="field">
            <span>Tickers</span>
            <input
              value={form.tickers}
              onChange={(event) => updateField("tickers", event.target.value)}
              spellCheck="false"
            />
          </label>

          <label className="field">
            <span>Optimizer</span>
            <select
              value={form.optimizer}
              onChange={(event) => updateField("optimizer", event.target.value)}
            >
              {OPTIMIZER_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <div className="field-grid">
            <label className="field">
              <span>Start</span>
              <input
                type="date"
                value={form.start}
                onChange={(event) => updateField("start", event.target.value)}
              />
            </label>
            <label className="field">
              <span>End</span>
              <input
                type="date"
                value={form.end}
                onChange={(event) => updateField("end", event.target.value)}
              />
            </label>
          </div>

          <div className="field-grid">
            <label className="field">
              <span>Risk-Free</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.005"
                value={form.riskFreeRate}
                onChange={(event) => updateField("riskFreeRate", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Max Weight</span>
              <input
                type="number"
                min="0.05"
                max="1"
                step="0.05"
                value={form.maxWeight}
                onChange={(event) => updateField("maxWeight", event.target.value)}
              />
            </label>
          </div>

          <div className="field-grid">
            <label className="field">
              <span>Trials</span>
              <input
                type="number"
                min="1000"
                step="1000"
                value={form.trials}
                onChange={(event) => updateField("trials", event.target.value)}
              />
            </label>
            <label className="field">
              <span>Benchmark</span>
              <input
                value={form.benchmark}
                onChange={(event) => updateField("benchmark", event.target.value.toUpperCase())}
                spellCheck="false"
              />
            </label>
          </div>

          <div className="field-grid">
            <label className="field">
              <span>MC Days</span>
              <input
                type="number"
                min="5"
                value={form.monteCarloDays}
                onChange={(event) => updateField("monteCarloDays", event.target.value)}
              />
            </label>
            <label className="field">
              <span>MC Sims</span>
              <input
                type="number"
                min="20"
                step="50"
                value={form.monteCarloSimulations}
                onChange={(event) => updateField("monteCarloSimulations", event.target.value)}
              />
            </label>
          </div>

          <button className="run-button" type="button" onClick={runAnalysis} disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
            <span>{loading ? "Running" : "Optimize"}</span>
          </button>

          {error && (
            <div className="error-box">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}
        </aside>

        <section className="analysis-surface">
          <header className="surface-header">
            <div>
              <h2>Portfolio Analysis</h2>
              <p>
                {optimization
                  ? `${MARKET_PRESETS[form.market].label}: ${optimization.price_rows} price rows, ${optimization.start} to ${optimization.end}`
                  : "Waiting for optimization run"}
              </p>
            </div>
            <button className="icon-button" type="button" title="Refresh status" onClick={() => window.location.reload()}>
              <RefreshCcw size={18} />
            </button>
          </header>

          <section className="metric-grid">
            <MetricCard icon={<Target size={20} />} label="Expected Return" value={formatPercent(optimization?.expected_return)} />
            <MetricCard icon={<Gauge size={20} />} label="Volatility" value={formatPercent(optimization?.volatility)} />
            <MetricCard icon={<BarChart3 size={20} />} label="Sharpe" value={optimization?.sharpe_ratio?.toFixed(3) ?? "n/a"} />
            <MetricCard icon={<ShieldAlert size={20} />} label="VaR 95%" value={formatPercent(risk?.historical_var_95)} />
          </section>

          <section className="chart-grid">
            <Panel title="Allocation" icon={<BarChart3 size={18} />}>
              {allocationData.length ? (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={allocationData} dataKey="weight" nameKey="ticker" innerRadius={58} outerRadius={92} paddingAngle={2}>
                      {allocationData.map((entry, index) => (
                        <Cell key={entry.ticker} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatPercent(value)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState />
              )}
            </Panel>

            <Panel title="Risk" icon={<ShieldAlert size={18} />}>
              {risk ? (
                <div className="risk-list">
                  <DataRow label="Historical VaR 95%" value={formatPercent(risk.historical_var_95)} />
                  <DataRow label="Parametric VaR 95%" value={formatPercent(risk.parametric_var_95)} />
                  <DataRow label="Max Drawdown" value={formatPercent(risk.max_drawdown)} />
                  <DataRow label="Annual Volatility" value={formatPercent(risk.annual_volatility)} />
                  <DataRow label="Beta" value={risk.beta?.toFixed(3) ?? "n/a"} />
                </div>
              ) : (
                <EmptyState />
              )}
            </Panel>

            <Panel title="Efficient Frontier" icon={<LineChart size={18} />} wide>
              {frontierData.length ? (
                <ResponsiveContainer width="100%" height={320}>
                  <ScatterChart margin={{ top: 16, right: 20, bottom: 20, left: 12 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      type="number"
                      dataKey="volatilityPct"
                      name="Risk"
                      unit="%"
                      tick={{ fontSize: 12 }}
                      label={{ value: "Volatility", position: "insideBottom", offset: -8 }}
                    />
                    <YAxis
                      type="number"
                      dataKey="returnPct"
                      name="Return"
                      unit="%"
                      tick={{ fontSize: 12 }}
                      label={{ value: "Expected Return", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip
                      formatter={(value, name) => [`${Number(value).toFixed(2)}%`, name]}
                      cursor={{ strokeDasharray: "3 3" }}
                    />
                    <Scatter name="Frontier" data={frontierData} fill="#2563eb" line shape="circle" />
                    {optimalPoint && (
                      <ReferenceDot
                        x={optimalPoint.volatilityPct}
                        y={optimalPoint.returnPct}
                        r={7}
                        fill="#dc2626"
                        stroke="white"
                      />
                    )}
                  </ScatterChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState />
              )}
            </Panel>

            <Panel title="Monte Carlo" icon={<Activity size={18} />} wide>
              {simulationData.length ? (
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={simulationData} margin={{ top: 16, right: 20, bottom: 12, left: 18 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                    <YAxis
                      tickFormatter={(value) => formatCompactCurrency(value, MARKET_PRESETS[form.market].currency)}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip formatter={(value) => formatCurrency(value, MARKET_PRESETS[form.market].currency)} />
                    <Area type="monotone" dataKey="p90" stroke="#16a34a" fill="#bbf7d0" fillOpacity={0.28} />
                    <Area type="monotone" dataKey="p75" stroke="#0891b2" fill="#bae6fd" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="p50" stroke="#2563eb" fill="none" strokeWidth={3} />
                    <Area type="monotone" dataKey="p25" stroke="#f59e0b" fill="#fde68a" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="p10" stroke="#dc2626" fill="#fecaca" fillOpacity={0.18} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState />
              )}
            </Panel>
          </section>
        </section>
      </section>
    </main>
  );
}

function MetricCard({ icon, label, value }) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function Panel({ title, icon, children, wide = false }) {
  return (
    <article className={wide ? "panel wide" : "panel"}>
      <header>
        <div>
          {icon}
          <h3>{title}</h3>
        </div>
      </header>
      {children}
    </article>
  );
}

function DataRow({ label, value }) {
  return (
    <div className="data-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty-state">
      <Activity size={22} />
      <span>No run loaded</span>
    </div>
  );
}
