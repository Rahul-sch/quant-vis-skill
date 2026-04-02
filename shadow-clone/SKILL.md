---
name: shadow-clone
description: "Scaffold a webhook-based trading signal interceptor that captures trade calls from Discord or Telegram, parses ticker/direction/price/stop-loss from natural language, and routes parsed signals to a paper trader or broker API. Use when a user asks to: (1) copy trades from a Discord or Telegram signal group, (2) build a webhook listener for trading signals, (3) auto-execute trades from chat messages, (4) parse trade calls into structured orders, (5) build a signal copier or trade relay server, (6) intercept guru calls or VIP signals automatically. Triggers on phrases like: copy trades, signal copier, webhook interceptor, trade relay, auto-execute signals, parse trade calls, Discord signals, Telegram signals."
---

# Shadow Clone

Scaffold a complete FastAPI signal interception server that captures trading signals from Discord/Telegram webhooks, parses them into structured orders, and routes to a paper trader or broker.

## What This Skill Produces

A `shadow-clone/` directory containing a runnable FastAPI server:

```
shadow-clone/
├── server.py               # FastAPI entry point
├── parser/
│   ├── signal_parser.py    # NLP signal parsing engine
│   ├── patterns.py         # Regex pattern library for trade formats
│   └── normalizer.py       # Ticker/direction/price normalization
├── router/
│   ├── paper_trader.py     # Built-in paper trading engine
│   ├── broker_base.py      # Abstract broker interface
│   └── alpaca_router.py    # Alpaca API integration (example)
├── webhooks/
│   ├── discord_hook.py     # Discord webhook receiver endpoint
│   └── telegram_hook.py    # Telegram webhook receiver endpoint
├── storage/
│   └── trade_log.py        # SQLite trade log
├── dashboard.py            # Optional Streamlit monitoring dashboard
├── config.py               # Configuration and env vars
├── requirements.txt
└── .env.example
```

## Workflow

### 1. Gather Requirements

- **Signal source?** Discord channel, Telegram group, or both.
- **Signal format examples?** Ask the user to paste 2-3 real signal messages from their group. This is critical for tuning the parser.
- **Execution target?** Paper trading (default, no API key), Alpaca, or custom broker.
- **Risk controls?** Max position size, daily loss limit, allowed tickers.

If the user has already described the signal format, extract from context.

### 2. Generate the Scaffold

Copy the template from `assets/template/` into the user's working directory as `shadow-clone/`. Then customize:

1. **`parser/patterns.py`** — Add regex patterns matching the user's specific signal group format. See `references/signal-formats.md` for common formats.
2. **`config.py`** — Set default risk limits, allowed tickers, execution mode.
3. **`router/`** — Keep only the routers the user needs (paper_trader always included).
4. **`webhooks/`** — Keep Discord, Telegram, or both based on user's source.

See `references/integration-guide.md` for detailed setup instructions per platform.

### 3. Install and Launch

```bash
cd shadow-clone
pip install -r requirements.txt
cp .env.example .env   # Edit with API keys if using a real broker
uvicorn server:app --host 0.0.0.0 --port 8000
```

The server starts and prints the webhook URL. User registers this URL in their Discord channel webhook settings or Telegram bot.

### 4. Test with Sample Signals

Use the built-in test endpoint:

```bash
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "BUY NVDA 170.00 SL 168.00 TP 175.00"}'
```

### 5. Iterate

User will request parser tuning ("my guru uses a different format"), new routers, or risk control adjustments. Edit only the affected module.

## Design Rules

- **Paper trader is always the default** — Never route to a live broker without explicit user opt-in and API key configuration.
- **Parse first, confirm second** — Log every parsed signal before execution. The trade log is the audit trail.
- **Fail safe** — If the parser cannot extract a ticker and direction with confidence, log the raw message and skip execution. Never guess.
- **Sub-200ms target** — The server should parse and route within 200ms. No heavy ML models in the hot path.
- **SQLite for storage** — Zero config, no database server needed.
- **Stateless webhook handlers** — Each incoming message is processed independently.

## Signal Parser Contract

The parser module must export:

```python
def parse_signal(message: str) -> ParsedSignal | None:
    """
    Returns ParsedSignal with: ticker, direction, entry_price,
    stop_loss, take_profit, confidence_score.
    Returns None if the message is not a trading signal.
    """
```

## Risk Control Rules

The router enforces these before execution:

1. **Max position size** — Configurable per-ticker and global.
2. **Daily loss limit** — Stop routing after hitting the daily P&L floor.
3. **Allowed tickers** — Whitelist mode. Only execute on known tickers.
4. **Cooldown** — Minimum seconds between executions on the same ticker.
5. **Duplicate detection** — Skip if an identical signal was received within N seconds.

## Reference Files

- `references/signal-formats.md` — Common signal message formats from popular Discord/Telegram groups, with regex patterns for each
- `references/integration-guide.md` — Step-by-step Discord webhook setup, Telegram bot setup, Alpaca API config, and localtunnel/ngrok exposure
