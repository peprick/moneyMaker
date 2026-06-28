from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field

from .config import DEFAULT_FRONTIER_POINTS
from .config import DEFAULT_FRONTIER_TRIALS
from .config import DEFAULT_INITIAL_VALUE
from .config import DEFAULT_MAX_WEIGHT
from .config import DEFAULT_MONTE_CARLO_DAYS
from .config import DEFAULT_MONTE_CARLO_SIMULATIONS
from .config import DEFAULT_OPTIMIZER_TRIALS
from .config import DEFAULT_RISK_FREE_RATE
from .config import DEFAULT_SEED
from .config import OptimizerName
from .frontier import efficient_frontier_points
from .market_data import fetch_adjusted_close_prices
from .monte_carlo import run_monte_carlo
from .optimizer import OptimizationConfig
from .optimizer import optimize_portfolio
from .risk import analyze_risk


app = FastAPI(title="Quant Portfolio Optimizer Engine")


class MarketDataRequest(BaseModel):
    tickers: list[str] = Field(min_length=1)
    start: str
    end: str | None = None
    market: Literal["us", "india"] = "us"


class OptimizeRequest(MarketDataRequest):
    objective: Literal["max_sharpe"] = "max_sharpe"
    optimizer: OptimizerName = OptimizerName.HIERARCHICAL_RISK_PARITY
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    max_weight: float = Field(default=DEFAULT_MAX_WEIGHT, gt=0, le=1)
    trials: int = Field(default=DEFAULT_OPTIMIZER_TRIALS, gt=0)
    seed: int = DEFAULT_SEED


class WeightedMarketDataRequest(MarketDataRequest):
    weights: dict[str, float]


class RiskRequest(WeightedMarketDataRequest):
    benchmark: str | None = None
    confidence: float = Field(default=0.95, gt=0, lt=1)


class FrontierRequest(MarketDataRequest):
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    max_weight: float = Field(default=DEFAULT_MAX_WEIGHT, gt=0, le=1)
    points: int = Field(default=DEFAULT_FRONTIER_POINTS, gt=1)
    trials: int = Field(default=DEFAULT_FRONTIER_TRIALS, gt=0)
    seed: int = DEFAULT_SEED


class MonteCarloRequest(WeightedMarketDataRequest):
    days: int = Field(default=DEFAULT_MONTE_CARLO_DAYS, gt=0)
    simulations: int = Field(default=DEFAULT_MONTE_CARLO_SIMULATIONS, gt=0)
    initial_value: float = Field(default=DEFAULT_INITIAL_VALUE, gt=0)
    seed: int = DEFAULT_SEED


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/optimize")
def optimize(request: OptimizeRequest) -> dict:
    try:
        prices = fetch_adjusted_close_prices(
            tickers=request.tickers,
            start=request.start,
            end=request.end,
            market=request.market,
        )
        result = optimize_portfolio(
            prices=prices,
            config=OptimizationConfig(
                objective=request.objective,
                optimizer=request.optimizer,
                risk_free_rate=request.risk_free_rate,
                max_weight=request.max_weight,
                trials=request.trials,
                seed=request.seed,
            ),
        )
        return {
            **asdict(result),
            "price_rows": len(prices),
            "start": str(prices.index.min().date()),
            "end": str(prices.index.max().date()),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/risk")
def risk(request: RiskRequest) -> dict:
    try:
        prices = fetch_adjusted_close_prices(
            tickers=request.tickers,
            start=request.start,
            end=request.end,
            market=request.market,
        )
        benchmark_prices = None
        if request.benchmark:
            benchmark_prices = fetch_adjusted_close_prices(
                tickers=[request.benchmark],
                start=request.start,
                end=request.end,
                market=request.market,
            )
        return asdict(
            analyze_risk(
                prices=prices,
                weights=request.weights,
                benchmark_prices=benchmark_prices,
                confidence=request.confidence,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/frontier")
def frontier(request: FrontierRequest) -> dict:
    try:
        prices = fetch_adjusted_close_prices(
            tickers=request.tickers,
            start=request.start,
            end=request.end,
            market=request.market,
        )
        points = efficient_frontier_points(
            prices=prices,
            risk_free_rate=request.risk_free_rate,
            max_weight=request.max_weight,
            points=request.points,
            trials=request.trials,
            seed=request.seed,
        )
        return {"points": [asdict(point) for point in points]}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/montecarlo")
def monte_carlo(request: MonteCarloRequest) -> dict:
    try:
        prices = fetch_adjusted_close_prices(
            tickers=request.tickers,
            start=request.start,
            end=request.end,
            market=request.market,
        )
        return asdict(
            run_monte_carlo(
                prices=prices,
                weights=request.weights,
                days=request.days,
                simulations=request.simulations,
                initial_value=request.initial_value,
                seed=request.seed,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
