"""Utility to generate trade marker DataFrames from a trade log.

This module converts a list of trades into the format expected by
candlestick.add_trade_markers().
"""

import pandas as pd


def trades_to_markers(trades: list[dict]) -> pd.DataFrame:
    """Convert a list of trade dicts to a markers DataFrame.

    Each trade dict should have:
        entry_date, exit_date, entry_price, exit_price, direction ('long'/'short')

    Returns DataFrame with columns: date, side, price
    """
    rows = []
    for t in trades:
        rows.append({
            "date": t["entry_date"],
            "side": "buy" if t["direction"] == "long" else "sell",
            "price": t["entry_price"],
        })
        rows.append({
            "date": t["exit_date"],
            "side": "sell" if t["direction"] == "long" else "buy",
            "price": t["exit_price"],
        })
    return pd.DataFrame(rows)


def generate_sample_trades(df: pd.DataFrame, n_trades: int = 10) -> pd.DataFrame:
    """Generate random sample trades for demo purposes.

    Useful for showing what the dashboard looks like before the user
    plugs in their real strategy.
    """
    import numpy as np

    if len(df) < n_trades * 5:
        n_trades = max(1, len(df) // 5)

    indices = sorted(np.random.choice(range(2, len(df) - 2), size=n_trades * 2, replace=False))
    rows = []
    for i in range(0, len(indices) - 1, 2):
        entry_idx = indices[i]
        exit_idx = indices[i + 1]
        direction = "long" if np.random.random() > 0.4 else "short"
        rows.append({
            "date": df.index[entry_idx],
            "side": "buy" if direction == "long" else "sell",
            "price": df["Close"].iloc[entry_idx],
        })
        rows.append({
            "date": df.index[exit_idx],
            "side": "sell" if direction == "long" else "buy",
            "price": df["Close"].iloc[exit_idx],
        })

    return pd.DataFrame(rows)
