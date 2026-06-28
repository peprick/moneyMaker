export const COLORS = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#7c3aed", "#0891b2"];

export const OPTIMIZER_OPTIONS = [
  { value: "hierarchical_risk_parity", label: "Hierarchical Risk Parity" },
  { value: "scipy_max_sharpe", label: "SciPy Max Sharpe" },
  { value: "black_litterman", label: "Black-Litterman" },
  { value: "random_search", label: "Random Search" }
];

export const MARKET_PRESETS = {
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

export const DEFAULT_ANALYSIS_SEED = 42;
export const MIN_FRONTIER_TRIALS = 2000;
export const FRONTIER_TRIAL_DIVISOR = 2;

export const DEFAULT_FORM = {
  market: "us",
  optimizer: "hierarchical_risk_parity",
  tickers: MARKET_PRESETS.us.tickers,
  start: "2023-01-01",
  end: "2026-01-01",
  benchmark: MARKET_PRESETS.us.benchmark,
  riskFreeRate: MARKET_PRESETS.us.riskFreeRate,
  maxWeight: 0.6,
  trials: 12000,
  frontierPoints: 8,
  monteCarloDays: 252,
  monteCarloSimulations: 600,
  initialValue: MARKET_PRESETS.us.initialValue
};
