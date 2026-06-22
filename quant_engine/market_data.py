from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf

SUPPORTED_MARKETS = {"us", "india"}


def _normalize_market(market: str | None) -> str:
    normalized_market = (market or "us").strip().lower()
    if normalized_market not in SUPPORTED_MARKETS:
        raise ValueError(f"unsupported market: {market}")
    return normalized_market


def _yahoo_ticker(ticker: str, market: str) -> str:
    normalized_ticker = ticker.strip().upper()
    if market == "india" and "." not in normalized_ticker and not normalized_ticker.startswith("^"):
        return f"{normalized_ticker}.NS"
    return normalized_ticker


def fetch_adjusted_close_prices(
    tickers: list[str],
    start: str | date,
    end: str | date | None = None,
    market: str = "us",
) -> pd.DataFrame:
    """Download a date-by-ticker adjusted close price table from Yahoo Finance."""
    if not tickers:
        raise ValueError("at least one ticker is required")

    normalized_market = _normalize_market(market)
    normalized_tickers = [ticker.strip().upper() for ticker in tickers if ticker.strip()]
    if not normalized_tickers:
        raise ValueError("at least one non-empty ticker is required")

    yahoo_tickers = [_yahoo_ticker(ticker, normalized_market) for ticker in normalized_tickers]
    display_names = dict(zip(yahoo_tickers, normalized_tickers))

    data = yf.download(
        tickers=yahoo_tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=True,
    )

    if data.empty:
        raise ValueError("no price data returned")

    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            prices = data["Adj Close"]
        elif "Close" in data.columns.get_level_values(0):
            prices = data["Close"]
        else:
            raise ValueError("downloaded data does not contain close prices")
    else:
        price_column = "Adj Close" if "Adj Close" in data.columns else "Close"
        if price_column not in data.columns:
            raise ValueError("downloaded data does not contain close prices")
        prices = data[[price_column]].rename(columns={price_column: normalized_tickers[0]})

    prices = prices.rename(columns=display_names)
    prices = prices.sort_index().dropna(how="any")
    if prices.empty:
        raise ValueError("all downloaded price rows had missing values")

    return prices
