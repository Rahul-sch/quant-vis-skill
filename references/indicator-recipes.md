# Indicator Recipes

Copy-paste recipes for common indicators following the module contract.

## Bollinger Bands

```python
def detect(df, period=20, std_dev=2.0):
    df = df.copy()
    df["bb_mid"] = df["Close"].rolling(period).mean()
    df["bb_upper"] = df["bb_mid"] + std_dev * df["Close"].rolling(period).std()
    df["bb_lower"] = df["bb_mid"] - std_dev * df["Close"].rolling(period).std()
    return df

def get_traces(df):
    """Return Plotly traces (not shapes) for Bollinger Bands."""
    import plotly.graph_objects as go
    return [
        go.Scatter(x=df.index, y=df["bb_upper"], name="BB Upper",
                   line=dict(color="rgba(255,255,255,0.3)", width=1)),
        go.Scatter(x=df.index, y=df["bb_lower"], name="BB Lower",
                   line=dict(color="rgba(255,255,255,0.3)", width=1),
                   fill="tonexty", fillcolor="rgba(255,255,255,0.03)"),
    ]
```

## VWAP

```python
def detect(df):
    df = df.copy()
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    df["vwap"] = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df
```

## RSI

```python
def detect(df, period=14):
    df = df.copy()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df
```

## MACD

```python
def detect(df, fast=12, slow=26, signal=9):
    df = df.copy()
    df["macd"] = df["Close"].ewm(span=fast).mean() - df["Close"].ewm(span=slow).mean()
    df["macd_signal"] = df["macd"].ewm(span=signal).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df
```

## Simple / Exponential Moving Averages

```python
def detect(df, sma_periods=[20, 50, 200], ema_periods=[9, 21]):
    df = df.copy()
    for p in sma_periods:
        df[f"sma_{p}"] = df["Close"].rolling(p).mean()
    for p in ema_periods:
        df[f"ema_{p}"] = df["Close"].ewm(span=p).mean()
    return df
```

## Order Blocks (simplified)

```python
def detect(df, pivot_len=5):
    """Identify order blocks at swing pivots with strong momentum."""
    import numpy as np
    df = df.copy()
    df["ob_type"] = None
    df["ob_top"] = np.nan
    df["ob_bottom"] = np.nan

    for i in range(pivot_len, len(df) - pivot_len):
        # Bullish OB: swing low followed by strong up move
        if df["Low"].iloc[i] == df["Low"].iloc[i-pivot_len:i+pivot_len+1].min():
            if df["Close"].iloc[i+1] > df["High"].iloc[i]:
                df.iloc[i, df.columns.get_loc("ob_type")] = "bullish"
                df.iloc[i, df.columns.get_loc("ob_top")] = df["High"].iloc[i]
                df.iloc[i, df.columns.get_loc("ob_bottom")] = df["Low"].iloc[i]

        # Bearish OB: swing high followed by strong down move
        if df["High"].iloc[i] == df["High"].iloc[i-pivot_len:i+pivot_len+1].max():
            if df["Close"].iloc[i+1] < df["Low"].iloc[i]:
                df.iloc[i, df.columns.get_loc("ob_type")] = "bearish"
                df.iloc[i, df.columns.get_loc("ob_top")] = df["High"].iloc[i]
                df.iloc[i, df.columns.get_loc("ob_bottom")] = df["Low"].iloc[i]

    return df
```

## ATR (Average True Range)

```python
def detect(df, period=14):
    df = df.copy()
    h_l = df["High"] - df["Low"]
    h_pc = (df["High"] - df["Close"].shift(1)).abs()
    l_pc = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    df["atr"] = tr.rolling(period).mean()
    return df
```
