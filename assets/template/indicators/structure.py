"""Market structure detection — Break of Structure (BOS) and Change of Character (CHoCH).

Uses swing high/low pivots to identify structural shifts.
"""

import pandas as pd
import numpy as np


def _find_pivots(df: pd.DataFrame, left: int = 5, right: int = 5) -> pd.DataFrame:
    """Identify swing highs and swing lows using pivot logic."""
    df = df.copy()
    df["swing_high"] = np.nan
    df["swing_low"] = np.nan

    highs = df["High"].values
    lows = df["Low"].values

    for i in range(left, len(df) - right):
        # Swing high: highest in window
        if highs[i] == max(highs[i - left : i + right + 1]):
            df.iloc[i, df.columns.get_loc("swing_high")] = highs[i]
        # Swing low: lowest in window
        if lows[i] == min(lows[i - left : i + right + 1]):
            df.iloc[i, df.columns.get_loc("swing_low")] = lows[i]

    return df


def detect(df: pd.DataFrame, pivot_left: int = 5, pivot_right: int = 5) -> pd.DataFrame:
    """Add structure columns: swing_high, swing_low, structure_break ('BOS' or 'CHoCH')."""
    df = _find_pivots(df, left=pivot_left, right=pivot_right)
    df["structure_break"] = None

    last_swing_high = None
    last_swing_low = None
    trend = None  # 'up' or 'down'

    for i in range(len(df)):
        sh = df["swing_high"].iloc[i]
        sl = df["swing_low"].iloc[i]

        if not np.isnan(sh) if isinstance(sh, (int, float)) else sh is not None:
            if last_swing_high is not None and sh > last_swing_high:
                if trend == "up":
                    df.iloc[i, df.columns.get_loc("structure_break")] = "BOS"
                elif trend == "down":
                    df.iloc[i, df.columns.get_loc("structure_break")] = "CHoCH"
                    trend = "up"
                else:
                    trend = "up"
            last_swing_high = sh

        if not np.isnan(sl) if isinstance(sl, (int, float)) else sl is not None:
            if last_swing_low is not None and sl < last_swing_low:
                if trend == "down":
                    df.iloc[i, df.columns.get_loc("structure_break")] = "BOS"
                elif trend == "up":
                    df.iloc[i, df.columns.get_loc("structure_break")] = "CHoCH"
                    trend = "down"
                else:
                    trend = "down"
            last_swing_low = sl

    return df


def get_shapes(df: pd.DataFrame, **params) -> list[dict]:
    """Return Plotly annotation dicts for BOS/CHoCH markers."""
    annotations = []
    for idx, row in df.iterrows():
        if row.get("structure_break") in ("BOS", "CHoCH"):
            price = row.get("swing_high") if not pd.isna(row.get("swing_high", np.nan)) else row.get("swing_low")
            if price is None or (isinstance(price, float) and np.isnan(price)):
                price = row["High"]
            color = "#00ff88" if row["structure_break"] == "BOS" else "#ff4444"
            annotations.append(dict(
                x=str(idx),
                y=price,
                text=row["structure_break"],
                showarrow=True,
                arrowhead=2,
                arrowcolor=color,
                font=dict(color=color, size=10),
                ax=0,
                ay=-30,
            ))
    return annotations
