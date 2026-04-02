# 📈 Quant-Vis

**Instant institutional-grade Streamlit dashboards for your trading strategies.**

## The Problem

The backtesting category on skills.sh has **5,700+ installs** — but every single skill gives you numbers in a terminal. No charts. No interactive visualization. No way to *see* where your entries and exits actually happened on the price chart.

## The Solution

Quant-Vis is an OpenClaw skill that scaffolds a **complete, runnable Streamlit dashboard** customized to your trading strategy. Not a template. Not a tutorial. Real code that runs immediately.

```
"Build me a dashboard for my FVG strategy"
         ↓ OpenClaw + Quant-Vis
    Full Streamlit app with:
    📊 Interactive candlestick charts
    🟢 Buy/sell arrows on your entries
    🟩 FVG rectangles highlighted
    📈 Equity curve + drawdown
    🎯 Sharpe, Profit Factor, Win Rate
```

## ✨ Features

- **📊 Interactive Plotly Charts** — Zoom, pan, hover on any candle
- **🟢🔴 Trade Markers** — Green △ buy / red ▽ sell arrows on the chart
- **🟩 FVG Detection** — Fair Value Gap rectangles with configurable sensitivity
- **📐 Market Structure** — BOS and CHoCH annotations with pivot logic
- **📈 Equity Curve** — Portfolio value over time with benchmark comparison
- **📉 Drawdown Plot** — Underwater equity visualization
- **🎯 Performance Stats** — Profit Factor, Sharpe, Win Rate, Max DD, Expectancy
- **📋 Trade Log** — Sortable, filterable table of all trades
- **🌙 Dark Theme** — Institutional look, screenshot-ready
- **🔌 Modular Indicators** — Add Bollinger Bands, RSI, VWAP with copy-paste recipes

## 🚀 Quick Start

```bash
cd quant-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501` — works on desktop and mobile.

## 🏗️ Generated Dashboard Structure

```
quant-dashboard/
├── app.py                  # Streamlit entry point
├── data/
│   └── loader.py           # yfinance + CSV data loading
├── charts/
│   ├── candlestick.py      # Plotly candlestick + overlays
│   ├── equity_curve.py     # Portfolio equity over time
│   ├── drawdown.py         # Underwater equity plot
│   └── trade_markers.py    # Buy/sell arrow generation
├── indicators/
│   ├── fvg.py              # Fair Value Gap detection
│   ├── structure.py        # BOS / CHoCH detection
│   └── custom.py           # Your indicators here
├── stats/
│   └── performance.py      # All performance metrics
└── requirements.txt
```

## 📊 Dashboard Panels

| Panel | What It Shows |
|-------|---------------|
| **Sidebar** | Ticker, date range, timeframe, indicator toggles, parameter sliders |
| **Candlestick Chart** | OHLCV with buy/sell arrows, FVG rectangles, BOS/CHoCH labels, volume |
| **Performance Cards** | Profit Factor, Sharpe, Win Rate, Max DD, Avg Win/Loss, Expectancy |
| **Equity Curve** | Portfolio value with optional benchmark overlay |
| **Drawdown** | Underwater equity (red fill) |
| **Trade Log** | Entry/exit dates, direction, prices, P&L |

## 🔧 Indicator System

Every indicator follows a simple contract:

```python
def detect(df: pd.DataFrame, **params) -> pd.DataFrame:
    """Add indicator columns to the DataFrame."""

def get_shapes(df: pd.DataFrame, **params) -> list[dict]:
    """Return Plotly shapes for chart overlays."""
```

Built-in indicators:
- **Fair Value Gaps (FVG)** — Bullish/bearish gap detection with configurable minimum gap %
- **Market Structure (BOS/CHoCH)** — Swing pivot-based structure breaks

Copy-paste recipes included for: Bollinger Bands, VWAP, RSI, MACD, Moving Averages, Order Blocks, ATR.

## 📦 Tech Stack

| Component | Library |
|-----------|---------|
| Frontend | Streamlit |
| Charts | Plotly |
| Data | yfinance (zero API keys) |
| Indicators | Custom modules |
| Stats | numpy / pandas |

## 📚 Reference Docs

- [Customization Guide](references/customization-guide.md) — How to adapt each module
- [Indicator Recipes](references/indicator-recipes.md) — Copy-paste code for BB, VWAP, RSI, MACD, OB, ATR

## 🧪 Tests

```
✅ All Python modules import clean
✅ yfinance data loading (102 rows SPY)
✅ FVG detection (42 gaps found)
✅ BOS/CHoCH detection working
✅ Chart generation (4 traces with overlays)
✅ Performance stats calculation
✅ Streamlit serves correctly
```

## License

MIT

---

*Built with [OpenClaw](https://openclaw.ai) • Companion to [Shadow Clone](https://github.com/Rahul-sch/shadow-clone-skill)*
