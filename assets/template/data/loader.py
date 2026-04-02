"""Data loading module — yfinance or CSV."""

import pandas as pd
import yfinance as yf


def load_yfinance(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data from yfinance.

    Returns DataFrame with columns: Open, High, Low, Close, Volume
    and a DatetimeIndex.
    """
    df = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
    if df.empty:
        return df
    # Flatten multi-level columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    # Ensure standard column names
    df = df.rename(columns={
        "Adj Close": "Adj_Close",
    })
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()


def load_csv(path: str, date_col: str = "Date") -> pd.DataFrame:
    """Load OHLCV data from a CSV file.

    Expects columns: Date (or datetime), Open, High, Low, Close, Volume.
    """
    df = pd.read_csv(path, parse_dates=[date_col], index_col=date_col)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            raise ValueError(f"CSV missing required column: {col}")
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()
