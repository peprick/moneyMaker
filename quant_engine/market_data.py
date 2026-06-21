from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf


def fetch_adjusted_close_prices(
    tickers: list[str],
    start: str | date,
    end: str | date | None = None,
) -> pd.DataFrame:
    """Download a date-by-ticker adjusted close price table from Yahoo Finance."""
    if not tickers:
        raise ValueError("at least one ticker is required")

    normalized_tickers = [ticker.strip().upper() for ticker in tickers if ticker.strip()]
    if not normalized_tickers:
        raise ValueError("at least one non-empty ticker is required")

    data = yf.download(
        tickers=normalized_tickers,
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

    prices = prices.sort_index().dropna(how="any")
    if prices.empty:
        raise ValueError("all downloaded price rows had missing values")

    return prices

