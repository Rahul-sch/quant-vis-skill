"""Drawdown visualization."""

import plotly.graph_objects as go
import pandas as pd
import numpy as np


def compute_drawdown(equity: pd.Series) -> pd.Series:
    """Compute drawdown series from equity curve.

    Returns Series of drawdown percentages (negative values).
    """
    peak = equity.cummax()
    drawdown = (equity - peak) / peak * 100
    return drawdown


def create_drawdown_chart(
    equity: pd.Series,
    title: str = "Drawdown",
    height: int = 250,
) -> go.Figure:
    """Plot underwater equity (drawdown) chart.

    Args:
        equity: Series of portfolio values indexed by date.
        title: Chart title.
        height: Chart height in pixels.
    """
    dd = compute_drawdown(equity)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dd.index,
        y=dd.values,
        name="Drawdown",
        line=dict(color="#ff4444", width=1),
        fill="tozeroy",
        fillcolor="rgba(255, 68, 68, 0.2)",
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color="#e0e0e0", size=14)),
        template="plotly_dark",
        height=height,
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#e0e0e0"),
        xaxis=dict(gridcolor="#2a2a2a"),
        yaxis=dict(title="Drawdown %", gridcolor="#2a2a2a"),
        margin=dict(l=60, r=60, t=40, b=30),
    )

    return fig
