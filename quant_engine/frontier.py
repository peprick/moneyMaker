from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .optimizer import annualized_covariance
from .optimizer import annualized_expected_returns
from .optimizer import daily_returns
from .optimizer import portfolio_metrics


@dataclass(frozen=True)
class FrontierPoint:
    target_return: float
    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: dict[str, float]


def efficient_frontier_points(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.04,
    max_weight: float = 0.60,
    points: int = 12,
    trials: int = 60_000,
    seed: int = 42,
) -> list[FrontierPoint]:
    if points <= 1:
        raise ValueError("points must be greater than 1")
    if trials <= 0:
        raise ValueError("trials must be positive")

    returns = daily_returns(prices)
    expected_returns = annualized_expected_returns(returns)
    covariance = annualized_covariance(returns)

    rng = np.random.default_rng(seed)
    candidates = []

    for _ in range(trials):
        weights = rng.random(len(expected_returns))
        weights = weights / weights.sum()

        if weights.max() > max_weight:
            continue

        candidates.append(
            portfolio_metrics(
                expected_returns=expected_returns,
                covariance=covariance,
                weights=weights,
                risk_free_rate=risk_free_rate,
            )
        )

    if not candidates:
        raise ValueError("no valid frontier candidates found")

    min_return = min(candidate.expected_return for candidate in candidates)
    max_return = max(candidate.expected_return for candidate in candidates)
    targets = np.linspace(min_return, max_return, points)

    frontier = []
    for target in targets:
        feasible = [
            candidate
            for candidate in candidates
            if candidate.expected_return >= float(target)
        ]
        if not feasible:
            continue

        best = min(feasible, key=lambda candidate: candidate.volatility)
        frontier.append(
            FrontierPoint(
                target_return=float(target),
                expected_return=best.expected_return,
                volatility=best.volatility,
                sharpe_ratio=best.sharpe_ratio,
                weights=best.weights,
            )
        )

    return frontier

