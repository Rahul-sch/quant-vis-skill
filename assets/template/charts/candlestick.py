"""Interactive Plotly candlestick chart with overlay support."""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def create_candlestick(
    df: pd.DataFrame,
    title: str = "",
    shapes: list[dict] | None = None,
    annotations: list[dict] | None = None,
    height: int = 700,
) -> go.Figure:
    """Build an interactive candlestick chart.

    Args:
        df: OHLCV DataFrame with DatetimeIndex.
        title: Chart title.
        shapes: List of Plotly shape dicts (FVG rectangles, S/R zones, etc.).
        annotations: List of Plotly annotation dicts (BOS/CHoCH labels, etc.).
        height: Chart height in pixels.
    """
    fig = go.Figure()

    # Candlestick trace
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price",
        increasing_line_color="#00ff88",
        decreasing_line_color="#ff4444",
        increasing_fillcolor="#00ff88",
        decreasing_fillcolor="#ff4444",
    ))

    # Volume as bar chart on secondary y-axis
    colors = ["#00ff88" if c >= o else "#ff4444" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["Volume"],
        name="Volume",
        marker_color=colors,
        opacity=0.3,
        yaxis="y2",
    ))

    # Add overlay shapes (FVG rectangles, etc.)
    if shapes:
        for shape in shapes:
            fig.add_shape(**shape)

    # Add annotations (BOS/CHoCH labels, etc.)
    if annotations:
        for ann in annotations:
            fig.add_annotation(**ann)

    fig.update_layout(
        title=dict(text=title, font=dict(color="#e0e0e0", size=18)),
        template="plotly_dark",
        height=height,
        xaxis=dict(
            rangeslider=dict(visible=False),
            gridcolor="#2a2a2a",
        ),
        yaxis=dict(
            title="Price",
            side="right",
            gridcolor="#2a2a2a",
        ),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="left",
            showgrid=False,
            range=[0, df["Volume"].max() * 4],  # Shrink volume bars
        ),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#e0e0e0"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=60, r=60, t=50, b=40),
    )

    return fig


def add_trade_markers(fig: go.Figure, trades: pd.DataFrame) -> go.Figure:
    """Add buy/sell arrows to an existing candlestick figure.

    Args:
        fig: Existing Plotly figure.
        trades: DataFrame with columns: date, side ('buy'/'sell'), price.
    """
    if trades.empty:
        return fig

    buys = trades[trades["side"] == "buy"]
    sells = trades[trades["side"] == "sell"]

    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys["date"],
            y=buys["price"],
            mode="markers",
            name="Buy",
            marker=dict(
                symbol="triangle-up",
                size=14,
                color="#00ff88",
                line=dict(width=1, color="#ffffff"),
            ),
        ))

    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells["date"],
            y=sells["price"],
            mode="markers",
            name="Sell",
            marker=dict(
                symbol="triangle-down",
                size=14,
                color="#ff4444",
                line=dict(width=1, color="#ffffff"),
            ),
        ))

    return fig
