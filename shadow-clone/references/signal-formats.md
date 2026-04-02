# Common Signal Formats

Real-world trading signal formats from popular Discord and Telegram groups. Use these to tune `parser/patterns.py`.

## Format 1: Standard (Most Common)

```
BUY NVDA 170.00 SL 168.00 TP 175.00
SELL TSLA 245.50 SL 248.00
LONG AAPL 190.00 SL 188.00 TP 195.00 TP2 200.00
SHORT SPY 520.00 SL 522.00
```

**Pattern:** `{DIRECTION} {TICKER} {PRICE} [SL {PRICE}] [TP {PRICE}]`
**Matched by:** `STANDARD_FORMAT`

## Format 2: Emoji-Heavy

```
NVDA 🟢 Buy @ 170.00 | SL: 168.00 | TP: 175.00
TSLA 🔴 Sell @ 245.50 | SL: 248.00
AAPL ⬆️ Long @ 190.00 | SL: 188.50 | TP: 195.00
```

**Pattern:** `{TICKER} {EMOJI} {DIRECTION} @ {PRICE} | SL: {PRICE} | TP: {PRICE}`
**Matched by:** `EMOJI_FORMAT`

## Format 3: Alert Style

```
🚀 NVDA Entry: 170.00 Stop: 168.00 Target: 175.00
⚠️ TSLA Price: 245.50 Stoploss: 248.00 Take Profit: 240.00
```

**Pattern:** `{TICKER} Entry: {PRICE} Stop: {PRICE} Target: {PRICE}`
**Matched by:** `ALERT_FORMAT`

## Format 4: Options Shorthand

```
$NVDA calls 170
$TSLA puts 245
$SPY calls 520 exp 4/18
```

**Pattern:** `${TICKER} {calls|puts} {STRIKE}`
**Matched by:** `OPTIONS_SHORTHAND`
**Note:** Maps calls to buy, puts to sell.

## Format 5: Conversational

```
Buying NVDA at 170, stop at 168
Going long AAPL at 190
Shorting TSLA at 245.50, stop at 248
```

**Pattern:** `{Buying|Selling|Going long|Shorting} {TICKER} at {PRICE}[, stop at {PRICE}]`
**Matched by:** `CONVERSATIONAL_FORMAT`

## Adding Custom Patterns

For a specific group's format, add a new pattern in `parser/patterns.py`:

```python
MY_GROUP_FORMAT = re.compile(
    r"(?P<direction>...)\s+(?P<ticker>...)\s+(?P<entry>...)",
    re.IGNORECASE,
)

# Add to ALL_PATTERNS list (earlier = higher priority)
ALL_PATTERNS.insert(0, ("my_group", MY_GROUP_FORMAT))
```

## Multi-Target Signals

Some groups post signals with multiple take-profit levels:

```
BUY NVDA 170.00 SL 168.00 TP1 172.00 TP2 175.00 TP3 180.00
```

The default parser captures the first TP only. To handle multiple TPs, extend the ParsedSignal dataclass and add a multi-TP pattern.

## Non-Signal Messages to Ignore

Common false positives the parser should skip:

- "NVDA is looking good today" (no price/direction)
- "Who's watching TSLA?" (question, not signal)
- "Closed NVDA for +5%" (exit report, not entry signal)
- "Market is bullish" (commentary)
- Emojis-only messages
- Memes and images
