"""Shadow Clone — Signal Interception Server.

Run with: uvicorn server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from config import config
from parser.signal_parser import parse_signal
from router.paper_trader import PaperTrader
from router.broker_base import BrokerBase
from storage.trade_log import TradeLog
from webhooks.discord_hook import router as discord_router
from webhooks.telegram_hook import router as telegram_router

# ─── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Shadow Clone",
    description="Trading signal interceptor — captures, parses, and executes signals from Discord/Telegram",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount webhook routers
app.include_router(discord_router)
app.include_router(telegram_router)

# ─── State ───────────────────────────────────────────────────────────────────

trade_log = TradeLog()
_last_execution: dict[str, float] = {}  # ticker -> timestamp for cooldown

# Initialize broker based on config
broker: BrokerBase
if config.EXECUTION_MODE == "alpaca" and config.ALPACA_API_KEY:
    from router.alpaca_router import AlpacaRouter
    broker = AlpacaRouter()
else:
    broker = PaperTrader()


# ─── Risk Checks ─────────────────────────────────────────────────────────────

def check_risk(ticker: str, direction: str, price: float) -> Optional[str]:
    """Run risk checks. Returns rejection reason or None if OK."""
    # Allowed tickers whitelist
    if config.ALLOWED_TICKERS and ticker not in config.ALLOWED_TICKERS:
        return f"Ticker {ticker} not in allowed list"

    # Position size check
    if price > config.MAX_POSITION_SIZE:
        return f"Price ${price:.2f} exceeds max position size ${config.MAX_POSITION_SIZE:.2f}"

    # Daily loss limit
    if isinstance(broker, PaperTrader) and broker.get_daily_pnl() < -config.DAILY_LOSS_LIMIT:
        return f"Daily loss limit reached (${config.DAILY_LOSS_LIMIT:.2f})"

    # Cooldown check
    last = _last_execution.get(ticker, 0)
    if time.time() - last < config.COOLDOWN_SECONDS:
        return f"Cooldown active for {ticker} ({config.COOLDOWN_SECONDS}s)"

    # Duplicate detection
    recent = trade_log.get_signal_by_ticker(ticker, within_seconds=config.DUPLICATE_WINDOW_SECONDS)
    if recent:
        return f"Duplicate signal for {ticker} within {config.DUPLICATE_WINDOW_SECONDS}s"

    return None


# ─── Signal Pipeline ─────────────────────────────────────────────────────────

class SignalPipelineResult(BaseModel):
    status: str
    signal: Optional[dict] = None
    execution: Optional[dict] = None
    rejection_reason: Optional[str] = None


def process_signal(message: str, source: str = "unknown") -> SignalPipelineResult:
    """Full signal pipeline: parse -> risk check -> execute -> log."""

    # 1. Parse
    parsed = parse_signal(message)
    if parsed is None:
        trade_log.log_signal(source=source, raw_message=message, status="unparseable")
        return SignalPipelineResult(status="unparseable")

    signal_data = {
        "ticker": parsed.ticker,
        "direction": parsed.direction,
        "entry_price": parsed.entry_price,
        "stop_loss": parsed.stop_loss,
        "take_profit": parsed.take_profit,
        "confidence": parsed.confidence,
        "pattern": parsed.pattern_name,
    }

    # 2. Confidence threshold
    if parsed.confidence < 0.5:
        signal_id = trade_log.log_signal(
            source=source, raw_message=message, ticker=parsed.ticker,
            direction=parsed.direction, entry_price=parsed.entry_price,
            stop_loss=parsed.stop_loss, take_profit=parsed.take_profit,
            confidence=parsed.confidence, pattern_name=parsed.pattern_name,
            status="low_confidence",
        )
        return SignalPipelineResult(
            status="low_confidence",
            signal=signal_data,
            rejection_reason=f"Confidence {parsed.confidence:.2f} below threshold 0.50",
        )

    # 3. Risk check
    price = parsed.entry_price or 0.0
    risk_rejection = check_risk(parsed.ticker, parsed.direction, price)
    if risk_rejection:
        signal_id = trade_log.log_signal(
            source=source, raw_message=message, ticker=parsed.ticker,
            direction=parsed.direction, entry_price=parsed.entry_price,
            stop_loss=parsed.stop_loss, take_profit=parsed.take_profit,
            confidence=parsed.confidence, pattern_name=parsed.pattern_name,
            status="risk_rejected",
        )
        return SignalPipelineResult(
            status="risk_rejected",
            signal=signal_data,
            rejection_reason=risk_rejection,
        )

    # 4. Log signal
    signal_id = trade_log.log_signal(
        source=source, raw_message=message, ticker=parsed.ticker,
        direction=parsed.direction, entry_price=parsed.entry_price,
        stop_loss=parsed.stop_loss, take_profit=parsed.take_profit,
        confidence=parsed.confidence, pattern_name=parsed.pattern_name,
        status="executing",
    )

    # 5. Execute
    quantity = max(1, int(config.MAX_POSITION_SIZE / price)) if price > 0 else 1
    result = broker.submit_order(
        ticker=parsed.ticker,
        direction=parsed.direction,
        quantity=quantity,
        entry_price=parsed.entry_price,
        stop_loss=parsed.stop_loss,
        take_profit=parsed.take_profit,
    )

    # 6. Log execution
    trade_log.log_execution(
        signal_id=signal_id,
        order_id=result.order_id,
        filled_price=result.filled_price,
        quantity=quantity,
        success=result.success,
        message=result.message,
    )

    _last_execution[parsed.ticker] = time.time()

    return SignalPipelineResult(
        status="executed" if result.success else "execution_failed",
        signal=signal_data,
        execution={
            "order_id": result.order_id,
            "filled_price": result.filled_price,
            "quantity": quantity,
            "message": result.message,
        },
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

class TestPayload(BaseModel):
    message: str
    source: str = "test"


@app.post("/test")
async def test_signal(payload: TestPayload):
    """Test endpoint — submit a signal message directly."""
    return process_signal(payload.message, source=payload.source)


@app.post("/process")
async def process_webhook_result(payload: dict):
    """Process the result from a webhook handler.

    Webhook endpoints (discord/telegram) return extracted messages.
    This endpoint runs them through the signal pipeline.
    Called internally or by a middleware.
    """
    message = payload.get("message", "")
    source = payload.get("source", "unknown")
    if not message:
        return {"status": "skipped", "reason": "no message"}
    return process_signal(message, source=source)


@app.get("/signals")
async def list_signals(limit: int = 50):
    """List recent signals."""
    return {"signals": trade_log.get_recent_signals(limit=limit)}


@app.get("/positions")
async def list_positions():
    """List current open positions (paper trader only)."""
    if isinstance(broker, PaperTrader):
        return {
            "positions": {t: broker.get_position(t) for t in broker.positions},
            "capital": broker.capital,
            "daily_pnl": broker.daily_pnl,
        }
    return {"message": "Position listing only available for paper trader"}


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "mode": config.EXECUTION_MODE,
        "broker": type(broker).__name__,
    }


@app.get("/")
async def root():
    return {
        "name": "Shadow Clone",
        "version": "1.0.0",
        "endpoints": {
            "POST /test": "Test signal parsing",
            "POST /webhook/discord": "Discord webhook receiver",
            "POST /webhook/telegram": "Telegram webhook receiver",
            "GET /signals": "List recent signals",
            "GET /positions": "Current positions",
            "GET /health": "Health check",
        },
    }
