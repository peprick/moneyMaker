from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .config import TRADING_DAYS_PER_YEAR
from .optimizer import daily_returns


@dataclass(frozen=True)
class RiskMetrics:
    historical_var_95: float
    parametric_var_95: float
    max_drawdown: float
    annual_volatility: float
    beta: float | None


def weights_series(weights: dict[str, float], columns: pd.Index) -> pd.Series:
    series = pd.Series(weights, dtype=float).reindex(columns).fillna(0.0)
    if np.any(series.values < 0):
        raise ValueError("weights cannot be negative")
    if not np.isclose(series.sum(), 1.0):
        raise ValueError("weights must sum to 1")
    return series


def portfolio_return_series(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    returns = daily_returns(prices)
    aligned_weights = weights_series(weights, returns.columns)
    return returns.dot(aligned_weights)


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    _validate_confidence(confidence)
    return float(np.percentile(returns, (1.0 - confidence) * 100))


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    _validate_confidence(confidence)
    mean = returns.mean()
    volatility = returns.std()
    z_score = stats.norm.ppf(1.0 - confidence)
    return float(mean + z_score * volatility)


def max_drawdown(returns: pd.Series) -> float:
    cumulative = (1.0 + returns).cumprod()
    running_peak = cumulative.cummax()
    drawdowns = (cumulative - running_peak) / running_peak
    return float(drawdowns.min())


def annual_volatility(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if aligned.empty:
        raise ValueError("portfolio and benchmark returns do not overlap")

    covariance = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])
    benchmark_variance = covariance[1, 1]
    if benchmark_variance == 0:
        raise ValueError("benchmark variance is zero")
    return float(covariance[0, 1] / benchmark_variance)


def analyze_risk(
    prices: pd.DataFrame,
    weights: dict[str, float],
    benchmark_prices: pd.DataFrame | None = None,
    confidence: float = 0.95,
) -> RiskMetrics:
    portfolio_returns = portfolio_return_series(prices, weights)
    beta_value = None

    if benchmark_prices is not None:
        benchmark_returns = daily_returns(benchmark_prices).iloc[:, 0]
        beta_value = beta(portfolio_returns, benchmark_returns)

    return RiskMetrics(
        historical_var_95=historical_var(portfolio_returns, confidence),
        parametric_var_95=parametric_var(portfolio_returns, confidence),
        max_drawdown=max_drawdown(portfolio_returns),
        annual_volatility=annual_volatility(portfolio_returns),
        beta=beta_value,
    )


def _validate_confidence(confidence: float) -> None:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
