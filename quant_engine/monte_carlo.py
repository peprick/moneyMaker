from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .risk import portfolio_return_series


@dataclass(frozen=True)
class MonteCarloResult:
    p10: list[float]
    p25: list[float]
    p50: list[float]
    p75: list[float]
    p90: list[float]
    final_p10: float
    final_p50: float
    final_p90: float


def run_monte_carlo(
    prices: pd.DataFrame,
    weights: dict[str, float],
    days: int = 252,
    simulations: int = 1_000,
    initial_value: float = 100_000.0,
    seed: int = 42,
) -> MonteCarloResult:
    if days <= 0:
        raise ValueError("days must be positive")
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    if initial_value <= 0:
        raise ValueError("initial_value must be positive")

    returns = portfolio_return_series(prices, weights)
    mean_daily_return = returns.mean()
    daily_volatility = returns.std()

    rng = np.random.default_rng(seed)
    drift = mean_daily_return - 0.5 * daily_volatility**2
    shocks = rng.normal(0.0, 1.0, size=(simulations, days))
    simulated_returns = np.exp(drift + daily_volatility * shocks)
    paths = initial_value * np.cumprod(simulated_returns, axis=1)

    return MonteCarloResult(
        p10=np.percentile(paths, 10, axis=0).tolist(),
        p25=np.percentile(paths, 25, axis=0).tolist(),
        p50=np.percentile(paths, 50, axis=0).tolist(),
        p75=np.percentile(paths, 75, axis=0).tolist(),
        p90=np.percentile(paths, 90, axis=0).tolist(),
        final_p10=float(np.percentile(paths[:, -1], 10)),
        final_p50=float(np.percentile(paths[:, -1], 50)),
        final_p90=float(np.percentile(paths[:, -1], 90)),
    )

