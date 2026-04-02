"""Equity curve chart."""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def create_equity_curve(
    equity: pd.Series,
    benchmark: pd.Series | None = None,
    title: str = "Equity Curve",
    height: int = 350,
) -> go.Figure:
    """Plot portfolio equity over time with optional benchmark.

    Args:
        equity: Series of portfolio values indexed by date.
        benchmark: Optional benchmark equity series for comparison.
        title: Chart title.
        height: Chart height in pixels.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=equity.index,
        y=equity.values,
        name="Strategy",
        line=dict(color="#00ff88", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 255, 136, 0.05)",
    ))

    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=benchmark.values,
            name="Benchmark",
            line=dict(color="#888888", width=1, dash="dot"),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(color="#e0e0e0", size=14)),
        template="plotly_dark",
        height=height,
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#e0e0e0"),
        xaxis=dict(gridcolor="#2a2a2a"),
        yaxis=dict(title="Portfolio Value ($)", gridcolor="#2a2a2a"),
        margin=dict(l=60, r=60, t=40, b=30),
    )

    return fig
