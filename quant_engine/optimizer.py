from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list
from scipy.cluster.hierarchy import linkage
from scipy.optimize import minimize
from scipy.spatial.distance import squareform

from .config import DEFAULT_MAX_WEIGHT
from .config import DEFAULT_RANDOM_SEARCH_TRIALS
from .config import DEFAULT_RISK_FREE_RATE
from .config import DEFAULT_SEED
from .config import DEFAULT_OPTIMIZER
from .config import OptimizerName
from .config import SUPPORTED_OPTIMIZERS
from .config import TRADING_DAYS_PER_YEAR

BLACK_LITTERMAN_TAU = 0.05
BLACK_LITTERMAN_VIEW_UNCERTAINTY = 4.0


@dataclass(frozen=True)
class PortfolioResult:
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float


@dataclass(frozen=True)
class OptimizationConfig:
    objective: str = "max_sharpe"
    optimizer: str = DEFAULT_OPTIMIZER
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    max_weight: float = DEFAULT_MAX_WEIGHT
    trials: int = DEFAULT_RANDOM_SEARCH_TRIALS
    seed: int = DEFAULT_SEED


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
        optimizer=_normalize_optimizer(optimizer if optimizer is not None else config.optimizer),
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

    if config.optimizer == OptimizerName.RANDOM_SEARCH.value:
        return _random_search_max_sharpe(
            expected_returns=expected_returns,
            covariance=covariance,
            config=config,
        )

    if config.optimizer == OptimizerName.HIERARCHICAL_RISK_PARITY.value:
        return _hierarchical_risk_parity(
            expected_returns=expected_returns,
            covariance=covariance,
            config=config,
        )

    if config.optimizer == OptimizerName.BLACK_LITTERMAN.value:
        expected_returns = _black_litterman_expected_returns(
            historical_expected_returns=expected_returns,
            covariance=covariance,
            risk_free_rate=config.risk_free_rate,
        )

    return _scipy_max_sharpe(
        expected_returns=expected_returns,
        covariance=covariance,
        config=config,
    )


def _normalize_optimizer(optimizer: str | OptimizerName) -> str:
    if isinstance(optimizer, OptimizerName):
        return optimizer.value
    return optimizer


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


def _hierarchical_risk_parity(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    config: OptimizationConfig,
) -> PortfolioResult:
    asset_count = len(expected_returns)
    if asset_count < 2:
        raise ValueError("HRP requires at least two tickers")
    _validate_feasible_weights(asset_count, config.max_weight)

    covariance_values = covariance.values
    volatility = np.sqrt(np.diag(covariance_values))
    if np.any(volatility <= 0):
        raise ValueError("asset volatility is zero; HRP is undefined")

    correlation = covariance_values / np.outer(volatility, volatility)
    correlation = np.nan_to_num(correlation, nan=0.0, posinf=0.0, neginf=0.0)
    correlation = np.clip(correlation, -1.0, 1.0)
    distance = np.sqrt((1.0 - correlation) / 2.0)
    np.fill_diagonal(distance, 0.0)

    ordered_indices = leaves_list(linkage(squareform(distance, checks=False), method="single")).tolist()
    weights = pd.Series(1.0, index=ordered_indices)
    clusters = [ordered_indices]

    while clusters:
        cluster = clusters.pop(0)
        if len(cluster) <= 1:
            continue

        split = len(cluster) // 2
        left_cluster = cluster[:split]
        right_cluster = cluster[split:]
        left_variance = _cluster_variance(covariance_values, left_cluster)
        right_variance = _cluster_variance(covariance_values, right_cluster)
        allocation = 1.0 - left_variance / (left_variance + right_variance)

        weights[left_cluster] *= allocation
        weights[right_cluster] *= 1.0 - allocation
        clusters.extend([left_cluster, right_cluster])

    ordered_weights = weights.sort_index().to_numpy(dtype=float)
    ordered_weights = _apply_max_weight_cap(ordered_weights / ordered_weights.sum(), config.max_weight)

    return portfolio_metrics(
        expected_returns=expected_returns,
        covariance=covariance,
        weights=ordered_weights,
        risk_free_rate=config.risk_free_rate,
    )


def _cluster_variance(covariance_values: np.ndarray, cluster: list[int]) -> float:
    cluster_covariance = covariance_values[np.ix_(cluster, cluster)]
    inverse_variance = 1.0 / np.diag(cluster_covariance)
    inverse_variance_weights = inverse_variance / inverse_variance.sum()
    return float(inverse_variance_weights.T @ cluster_covariance @ inverse_variance_weights)


def _apply_max_weight_cap(weights: np.ndarray, max_weight: float) -> np.ndarray:
    capped_weights = np.minimum(weights, max_weight)
    remaining_weight = 1.0 - capped_weights.sum()
    if remaining_weight <= 1e-12:
        return capped_weights / capped_weights.sum()

    available_room = max_weight - capped_weights
    if available_room.sum() + 1e-12 < remaining_weight:
        raise ValueError("max_weight is too low to allocate 100% across the selected tickers")

    capped_weights += available_room / available_room.sum() * remaining_weight
    return capped_weights / capped_weights.sum()


def _black_litterman_expected_returns(
    historical_expected_returns: pd.Series,
    covariance: pd.DataFrame,
    risk_free_rate: float,
) -> pd.Series:
    asset_count = len(historical_expected_returns)
    market_weights = np.full(asset_count, 1.0 / asset_count)
    covariance_values = covariance.values

    market_return = float(np.dot(market_weights, historical_expected_returns.values))
    market_variance = float(market_weights.T @ covariance_values @ market_weights)
    if market_variance <= 0:
        raise ValueError("market proxy variance is zero; Black-Litterman is undefined")

    risk_aversion = max((market_return - risk_free_rate) / market_variance, 1e-6)
    equilibrium_returns = risk_aversion * covariance_values @ market_weights

    tau_covariance = BLACK_LITTERMAN_TAU * covariance_values
    view_pick_matrix = np.eye(asset_count)
    view_returns = historical_expected_returns.values
    view_uncertainty = np.diag(np.diag(tau_covariance)) * BLACK_LITTERMAN_VIEW_UNCERTAINTY

    prior_precision = np.linalg.pinv(tau_covariance)
    view_precision = np.linalg.pinv(view_uncertainty)
    posterior_covariance = np.linalg.pinv(
        prior_precision + view_pick_matrix.T @ view_precision @ view_pick_matrix
    )
    posterior_returns = posterior_covariance @ (
        prior_precision @ equilibrium_returns
        + view_pick_matrix.T @ view_precision @ view_returns
    )

    return pd.Series(
        posterior_returns,
        index=historical_expected_returns.index,
        name="black_litterman_expected_return",
    )


def _scipy_max_sharpe(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    config: OptimizationConfig,
) -> PortfolioResult:
    asset_count = len(expected_returns)
    _validate_feasible_weights(asset_count, config.max_weight)

    bounds = [(0.0, config.max_weight) for _ in range(asset_count)]
    constraints = ({"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0},)

    def negative_sharpe(weights: np.ndarray) -> float:
        expected_return = float(np.dot(weights, expected_returns.values))
        variance = float(weights.T @ covariance.values @ weights)
        volatility = float(np.sqrt(max(variance, 0.0)))
        if volatility <= 0:
            return 1e9
        return -((expected_return - config.risk_free_rate) / volatility)

    best: PortfolioResult | None = None
    failure_messages: list[str] = []

    for initial_weights in _initial_weight_candidates(covariance, config):
        result = minimize(
            negative_sharpe,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1_000, "ftol": 1e-9},
        )

        if not result.success:
            failure_messages.append(str(result.message))
            continue

        weights = np.asarray(result.x, dtype=float)
        weights[np.isclose(weights, 0.0, atol=1e-10)] = 0.0
        weights = weights / weights.sum()
        if weights.max() > config.max_weight + 1e-8:
            continue

        candidate = portfolio_metrics(
            expected_returns=expected_returns,
            covariance=covariance,
            weights=weights,
            risk_free_rate=config.risk_free_rate,
        )
        if best is None or candidate.sharpe_ratio > best.sharpe_ratio:
            best = candidate

    if best is None:
        messages = "; ".join(sorted(set(failure_messages))) or "no feasible solution"
        raise ValueError(f"SciPy optimizer failed: {messages}")

    return best


def _initial_weight_candidates(
    covariance: pd.DataFrame,
    config: OptimizationConfig,
) -> list[np.ndarray]:
    asset_count = len(covariance)
    equal_weights = np.full(asset_count, 1.0 / asset_count)
    inverse_variance = 1.0 / np.diag(covariance.values)
    inverse_variance_weights = inverse_variance / inverse_variance.sum()

    candidates = [
        equal_weights,
        _apply_max_weight_cap(inverse_variance_weights, config.max_weight),
    ]

    rng = np.random.default_rng(config.seed)
    for _ in range(min(config.trials, 25)):
        random_weights = rng.random(asset_count)
        random_weights = random_weights / random_weights.sum()
        candidates.append(_apply_max_weight_cap(random_weights, config.max_weight))

    return candidates
