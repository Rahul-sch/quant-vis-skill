# Customization Guide

How to adapt each module when scaffolding a dashboard for a specific user strategy.

## app.py Customization

- **Default ticker**: Change `value="SPY"` to user's preferred instrument.
- **Default timeframe**: Change the `selectbox` index to match user's trading timeframe.
- **Sidebar controls**: Add/remove indicator checkboxes and parameter sliders.
- **Strategy-specific sections**: Replace "Demo Trades" with the user's actual strategy logic.

## data/loader.py Customization

- **CSV mode**: If user has a CSV, switch `fetch_data()` in app.py to call `load_csv()`.
- **API mode**: Add a new function for user's data provider (Alpaca, Polygon, etc.). Match the same return signature: DataFrame with Open, High, Low, Close, Volume and DatetimeIndex.
- **Crypto**: yfinance supports crypto tickers like `BTC-USD`, `ETH-USD`.

## indicators/ Customization

### Adding a New Indicator

1. Create `indicators/my_indicator.py`
2. Implement `detect(df, **params) -> pd.DataFrame` — adds columns to df
3. Optionally implement `get_shapes(df, **params) -> list[dict]` for chart overlays
4. Import in app.py, add sidebar checkbox, wire into the processing section

### Common Indicators to Add

| Indicator | Overlay Type | Implementation Notes |
|-----------|-------------|---------------------|
| Bollinger Bands | Lines on chart | `add_trace(go.Scatter(...))` for upper/lower bands |
| VWAP | Line on chart | Cumulative (price × volume) / cumulative volume |
| RSI | Separate subplot | Use `make_subplots(rows=2)` for RSI panel below price |
| MACD | Separate subplot | Signal line + histogram in subplot |
| Moving Averages | Lines on chart | `df["Close"].rolling(period).mean()` |
| Order Blocks | Rectangles | Similar to FVG shapes but at swing pivot candles |

### FVG Tuning

- `min_gap_pct`: Filter out tiny gaps. 0.1% works well for stocks, 0.5% for crypto.
- Modify `lookback` in `get_shapes()` to control how many historical FVGs display.

### Structure (BOS/CHoCH) Tuning

- `pivot_left` / `pivot_right`: Higher values = fewer, more significant pivots. 5 is default, 10+ for swing trading.

## charts/ Customization

### Candlestick Colors

In `charts/candlestick.py`, modify:
- `increasing_line_color` / `increasing_fillcolor` for bull candles
- `decreasing_line_color` / `decreasing_fillcolor` for bear candles

### Adding Subplots (RSI, MACD panels)

Replace `go.Figure()` with `make_subplots(rows=N, cols=1, shared_xaxes=True, row_heights=[...])`. Put price in row 1, RSI in row 2, etc.

### Chart Height

Adjust `height` parameter. Default 700px for main chart, 350px for equity, 250px for drawdown.

## stats/ Customization

### Custom Metrics

Add new metrics to `compute_stats()` return dict. They automatically appear as stat cards in the dashboard.

### Initial Capital

Default $100,000. Change in `compute_stats()` and `compute_equity_series()` calls.

## Plugging In Real Strategy Trades

Replace the demo trade generation in app.py with actual strategy output:

```python
# Instead of generate_sample_trades(), load real trades:
trades = [
    {"entry_date": "2024-01-15", "exit_date": "2024-01-16",
     "entry_price": 470.50, "exit_price": 475.20,
     "direction": "long", "quantity": 100},
    # ... more trades
]
```

Or load from CSV/JSON:

```python
trades = pd.read_csv("my_trades.csv").to_dict("records")
```
