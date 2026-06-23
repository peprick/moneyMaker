from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace

import numpy as np
import pandas as pd
from scipy.optimize import minimize


TRADING_DAYS_PER_YEAR = 252
SUPPORTED_OPTIMIZERS = {"random_search", "scipy_max_sharpe"}


@dataclass(frozen=True)
class PortfolioResult:
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float


@dataclass(frozen=True)
class OptimizationConfig:
    objective: str = "max_sharpe"
    optimizer: str = "scipy_max_sharpe"
    risk_free_rate: float = 0.04
    max_weight: float = 0.60
    trials: int = 20_000
    seed: int = 42


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert a date-by-ticker price table into daily percentage returns."""
    if prices.empty:
        raise ValueError("prices cannot be empty")
    if len(prices) < 3:
        raise ValueError("at least 3 price rows are required")
    if prices.isna().any().any():
        raise ValueError("prices cannot contain missing values")

    returns = prices.pct_change().dropna()
    if returns.empty:
        raise ValueError("not enough price movement to calculate returns")
    return returns


def annualized_expected_returns(returns: pd.DataFrame) -> pd.Series:
    return returns.mean() * TRADING_DAYS_PER_YEAR


def annualized_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.cov() * TRADING_DAYS_PER_YEAR


def portfolio_metrics(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    weights: np.ndarray,
    risk_free_rate: float = 0.04,
) -> PortfolioResult:
    tickers = list(expected_returns.index)
    weights = np.asarray(weights, dtype=float)

    if len(weights) != len(tickers):
        raise ValueError("weights length must match number of tickers")
    if np.any(weights < 0):
        raise ValueError("this optimizer only supports long-only weights")
    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("weights must sum to 1")

    expected_return = float(np.dot(weights, expected_returns.values))
    variance = float(weights.T @ covariance.values @ weights)
    volatility = float(np.sqrt(max(variance, 0.0)))
    if volatility == 0:
        raise ValueError("portfolio volatility is zero; Sharpe ratio is undefined")

    return PortfolioResult(
        weights={ticker: float(weight) for ticker, weight in zip(tickers, weights)},
        expected_return=expected_return,
        volatility=volatility,
        sharpe_ratio=float((expected_return - risk_free_rate) / volatility),
    )


def optimize_portfolio(
    prices: pd.DataFrame,
    config: OptimizationConfig | None = None,
    *,
    objective: str | None = None,
    optimizer: str | None = None,
    risk_free_rate: float | None = None,
    max_weight: float | None = None,
    trials: int | None = None,
    seed: int | None = None,
) -> PortfolioResult:
    """Stable optimizer facade used by the API and future Java backend."""
    config = config or OptimizationConfig()
    config = replace(
        config,
        objective=objective if objective is not None else config.objective,
        optimizer=optimizer if optimizer is not None else config.optimizer,
        risk_free_rate=(
            risk_free_rate if risk_free_rate is not None else config.risk_free_rate
        ),
        max_weight=max_weight if max_weight is not None else config.max_weight,
        trials=trials if trials is not None else config.trials,
        seed=seed if seed is not None else config.seed,
    )

    _validate_config(config)

    returns = daily_returns(prices)
    expected_returns = annualized_expected_returns(returns)
    covariance = annualized_covariance(returns)

    if config.objective != "max_sharpe":
        raise NotImplementedError(f"unsupported objective: {config.objective}")
    if config.optimizer not in SUPPORTED_OPTIMIZERS:
        raise NotImplementedError(f"unsupported optimizer: {config.optimizer}")

    if config.optimizer == "random_search":
        return _random_search_max_sharpe(
            expected_returns=expected_returns,
            covariance=covariance,
            config=config,
        )

    return _scipy_max_sharpe(
        expected_returns=expected_returns,
        covariance=covariance,
        config=config,
    )


def _validate_config(config: OptimizationConfig) -> None:
    if not 0 < config.max_weight <= 1:
        raise ValueError("max_weight must be greater than 0 and less than or equal to 1")
    if config.trials <= 0:
        raise ValueError("trials must be positive")
    if not np.isfinite(config.risk_free_rate):
        raise ValueError("risk_free_rate must be finite")


def _validate_feasible_weights(asset_count: int, max_weight: float) -> None:
    if asset_count * max_weight < 1:
        raise ValueError("max_weight is too low to allocate 100% across the selected tickers")


def _random_search_max_sharpe(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    config: OptimizationConfig,
) -> PortfolioResult:
    _validate_feasible_weights(len(expected_returns), config.max_weight)

    rng = np.random.default_rng(config.seed)
    best: PortfolioResult | None = None

    for _ in range(config.trials):
        weights = rng.random(len(expected_returns))
        weights = weights / weights.sum()

        if weights.max() > config.max_weight:
            continue

        result = portfolio_metrics(
            expected_returns=expected_returns,
            covariance=covariance,
            weights=weights,
            risk_free_rate=config.risk_free_rate,
        )

        if best is None or result.sharpe_ratio > best.sharpe_ratio:
            best = result

    if best is None:
        raise ValueError("no valid portfolio found; relax constraints or increase trials")

    return best


def _scipy_max_sharpe(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    config: OptimizationConfig,
) -> PortfolioResult:
    asset_count = len(expected_returns)
    _validate_feasible_weights(asset_count, config.max_weight)

    bounds = [(0.0, config.max_weight) for _ in range(asset_count)]
    constraints = ({"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0},)
    initial_weights = np.full(asset_count, 1.0 / asset_count)

    def negative_sharpe(weights: np.ndarray) -> float:
        expected_return = float(np.dot(weights, expected_returns.values))
        variance = float(weights.T @ covariance.values @ weights)
        volatility = float(np.sqrt(max(variance, 0.0)))
        if volatility <= 0:
            return 1e9
        return -((expected_return - config.risk_free_rate) / volatility)

    result = minimize(
        negative_sharpe,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1_000, "ftol": 1e-9},
    )

    if not result.success:
        raise ValueError(f"SciPy optimizer failed: {result.message}")

    weights = np.asarray(result.x, dtype=float)
    weights[np.isclose(weights, 0.0, atol=1e-10)] = 0.0
    weights = weights / weights.sum()

    return portfolio_metrics(
        expected_returns=expected_returns,
        covariance=covariance,
        weights=weights,
        risk_free_rate=config.risk_free_rate,
    )
