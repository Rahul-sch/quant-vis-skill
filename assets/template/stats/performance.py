"""Performance statistics for trading strategies."""

import pandas as pd
import numpy as np


def compute_stats(trades: list[dict], initial_capital: float = 100_000) -> dict:
    """Compute performance statistics from a list of trades.

    Each trade dict should have:
        entry_price, exit_price, direction ('long'/'short'), quantity (default 1)

    Returns dict with all key performance metrics.
    """
    if not trades:
        return _empty_stats()

    pnls = []
    for t in trades:
        qty = t.get("quantity", 1)
        if t["direction"] == "long":
            pnl = (t["exit_price"] - t["entry_price"]) * qty
        else:
            pnl = (t["entry_price"] - t["exit_price"]) * qty
        pnls.append(pnl)

    pnls = np.array(pnls)
    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]

    total_pnl = pnls.sum()
    win_rate = len(wins) / len(pnls) * 100 if len(pnls) > 0 else 0
    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) > 0 and losses.sum() != 0 else float("inf")

    # Equity curve for Sharpe / max drawdown
    equity = np.cumsum(pnls) + initial_capital
    peak = np.maximum.accumulate(equity)
    drawdowns = (equity - peak) / peak * 100
    max_drawdown = drawdowns.min()

    # Daily returns proxy (per-trade returns)
    returns = pnls / initial_capital
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

    expectancy = pnls.mean() if len(pnls) > 0 else 0

    return {
        "Total P&L": f"${total_pnl:,.2f}",
        "Total Trades": len(pnls),
        "Win Rate": f"{win_rate:.1f}%",
        "Profit Factor": f"{profit_factor:.2f}" if profit_factor != float("inf") else "∞",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_drawdown:.1f}%",
        "Avg Win": f"${avg_win:,.2f}",
        "Avg Loss": f"${avg_loss:,.2f}",
        "Expectancy": f"${expectancy:,.2f}",
    }


def _empty_stats() -> dict:
    return {
        "Total P&L": "$0.00",
        "Total Trades": 0,
        "Win Rate": "0.0%",
        "Profit Factor": "N/A",
        "Sharpe Ratio": "0.00",
        "Max Drawdown": "0.0%",
        "Avg Win": "$0.00",
        "Avg Loss": "$0.00",
        "Expectancy": "$0.00",
    }


def compute_equity_series(trades: list[dict], initial_capital: float = 100_000) -> pd.Series:
    """Build an equity curve Series from trades.

    Returns Series indexed by trade number with portfolio value.
    """
    equity = [initial_capital]
    for t in trades:
        qty = t.get("quantity", 1)
        if t["direction"] == "long":
            pnl = (t["exit_price"] - t["entry_price"]) * qty
        else:
            pnl = (t["entry_price"] - t["exit_price"]) * qty
        equity.append(equity[-1] + pnl)

    return pd.Series(equity, name="Equity")
