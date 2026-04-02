---
name: quant-vis
description: "Generate institutional-grade Streamlit trading dashboards with interactive Plotly charts. Use when a user asks to: (1) visualize a trading strategy or backtest results, (2) build a quant dashboard or trading dashboard, (3) create candlestick charts with trade entry/exit markers, (4) visualize Fair Value Gaps (FVG), Smart Money Concepts (BOS, CHoCH), or any technical indicator overlays, (5) scaffold a Streamlit app for financial data, (6) see equity curves, drawdown plots, or performance stats for a strategy. Triggers on phrases like: build me a dashboard, visualize my strategy, quant dashboard, trading visualization, show my backtest, candlestick chart, FVG chart, equity curve, Streamlit trading app."
---

# Quant-Vis

Scaffold a complete, runnable Streamlit trading dashboard customized to the user's strategy.

## What This Skill Produces

A `quant-dashboard/` directory containing a fully working Streamlit app:

```
quant-dashboard/
├── app.py                  # Entry point — streamlit run app.py
├── data/
│   └── loader.py           # Data fetching (yfinance / CSV)
├── charts/
│   ├── candlestick.py      # Plotly candlestick + overlays
│   ├── equity_curve.py     # Portfolio equity over time
│   ├── drawdown.py         # Underwater equity plot
│   └── trade_markers.py    # Entry/exit arrows on chart
├── indicators/
│   ├── fvg.py              # Fair Value Gap detection
│   ├── structure.py        # BOS / CHoCH detection
│   └── custom.py           # Placeholder for user indicators
├── stats/
│   └── performance.py      # Sharpe, PF, win rate, max DD, etc.
└── requirements.txt
```

## Workflow

### 1. Gather Requirements (ask only what's needed)

- **Strategy type?** FVG, momentum, mean reversion, SMC, custom — determines which indicator modules to include.
- **Data source?** yfinance ticker (default), CSV file path, or API endpoint.
- **Timeframe?** 1m, 5m, 15m, 1H, 4H, 1D (default: 1D).
- **Extra overlays?** Bollinger Bands, moving averages, VWAP, RSI panel, etc.

If the user already described their strategy in conversation, don't re-ask — extract from context.

### 2. Generate the Scaffold

Copy the template from `assets/template/` into the user's working directory as `quant-dashboard/`. Then customize:

1. **`app.py`** — Set default ticker, timeframe, and sidebar controls matching user's strategy.
2. **`indicators/`** — Keep only the modules the user needs. Add custom indicator logic if described.
3. **`charts/candlestick.py`** — Wire up the correct overlays (FVG rectangles, trade arrows, bands, etc.).
4. **`stats/performance.py`** — Always include. No customization needed.
5. **`data/loader.py`** — Switch between yfinance or CSV based on user's data source.

See `references/customization-guide.md` for detailed instructions on adapting each module.

### 3. Install & Launch

```bash
cd quant-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Report the local URL (typically `http://localhost:8501`) to the user.

### 4. Iterate

User will request changes ("add Bollinger Bands", "change colors", "add RSI panel"). Edit only the affected module — never regenerate the full scaffold.

## Design Rules

- **Dark theme by default** — Use `st.set_page_config(layout="wide")` with custom dark CSS in `app.py`.
- **Plotly only** — No matplotlib. Interactive zoom/pan/hover is mandatory for traders.
- **yfinance default** — Zero API keys needed out of the box.
- **Trade markers are the hero feature** — Green △ buy arrows, red ▽ sell arrows on the candlestick chart.
- **Performance stats always visible** — Never hide behind a tab or expander.
- **Modular indicators** — Each indicator is a separate file returning a DataFrame or list of annotations.

## Indicator Module Contract

Every indicator module in `indicators/` must export a function with this signature:

```python
def detect(df: pd.DataFrame, **params) -> pd.DataFrame:
    """
    Input: OHLCV DataFrame with columns: Open, High, Low, Close, Volume
    Output: Same DataFrame with added columns for the indicator
    """
```

For overlay indicators (FVG rectangles, S/R zones), also export:

```python
def get_shapes(df: pd.DataFrame, **params) -> list[dict]:
    """Return list of Plotly shape dicts for add_shape()."""
```

## Reference Files

- `references/customization-guide.md` — Detailed guide for adapting each module to different strategies
- `references/indicator-recipes.md` — Code patterns for common indicators (FVG, BOS, CHoCH, BB, VWAP, RSI, MACD)
