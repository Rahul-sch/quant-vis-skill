"""Fair Value Gap (FVG) detection.

A bullish FVG forms when candle[i-2].high < candle[i].low (gap up).
A bearish FVG forms when candle[i-2].low > candle[i].high (gap down).
"""

import pandas as pd


def detect(df: pd.DataFrame, min_gap_pct: float = 0.0) -> pd.DataFrame:
    """Add FVG columns to the DataFrame.

    Added columns:
        fvg_type: 'bullish', 'bearish', or NaN
        fvg_top: upper boundary of the gap
        fvg_bottom: lower boundary of the gap
    """
    df = df.copy()
    df["fvg_type"] = None
    df["fvg_top"] = None
    df["fvg_bottom"] = None

    for i in range(2, len(df)):
        high_2 = df["High"].iloc[i - 2]
        low_2 = df["Low"].iloc[i - 2]
        low_0 = df["Low"].iloc[i]
        high_0 = df["High"].iloc[i]

        # Bullish FVG: gap between candle[i-2] high and candle[i] low
        if low_0 > high_2:
            gap_size = (low_0 - high_2) / high_2
            if gap_size >= min_gap_pct:
                df.iloc[i, df.columns.get_loc("fvg_type")] = "bullish"
                df.iloc[i, df.columns.get_loc("fvg_top")] = low_0
                df.iloc[i, df.columns.get_loc("fvg_bottom")] = high_2

        # Bearish FVG: gap between candle[i] high and candle[i-2] low
        elif high_0 < low_2:
            gap_size = (low_2 - high_0) / low_2
            if gap_size >= min_gap_pct:
                df.iloc[i, df.columns.get_loc("fvg_type")] = "bearish"
                df.iloc[i, df.columns.get_loc("fvg_top")] = low_2
                df.iloc[i, df.columns.get_loc("fvg_bottom")] = high_0

    return df


def get_shapes(df: pd.DataFrame, lookback: int = 50, **params) -> list[dict]:
    """Return Plotly shape dicts for FVG rectangles.

    Args:
        df: DataFrame with fvg_type, fvg_top, fvg_bottom columns (from detect()).
        lookback: Only show FVGs from the last N bars.
    """
    df_recent = df.iloc[-lookback:] if len(df) > lookback else df
    shapes = []
    dates = df_recent.index

    for i, (idx, row) in enumerate(df_recent.iterrows()):
        if row.get("fvg_type") is None or pd.isna(row.get("fvg_type")):
            continue

        color = "rgba(0, 255, 136, 0.15)" if row["fvg_type"] == "bullish" else "rgba(255, 68, 68, 0.15)"
        border = "rgba(0, 255, 136, 0.5)" if row["fvg_type"] == "bullish" else "rgba(255, 68, 68, 0.5)"

        # Extend rectangle 5 bars forward (or to end of data)
        end_idx = min(i + 5, len(dates) - 1)

        shapes.append(dict(
            type="rect",
            x0=str(idx),
            x1=str(dates[end_idx]),
            y0=row["fvg_bottom"],
            y1=row["fvg_top"],
            fillcolor=color,
            line=dict(color=border, width=1),
            layer="below",
        ))

    return shapes
