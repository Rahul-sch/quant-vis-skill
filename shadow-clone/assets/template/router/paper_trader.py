"""Built-in paper trading engine. No API keys needed."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional
import uuid

from .broker_base import BrokerBase, OrderResult


@dataclass
class PaperPosition:
    ticker: str
    direction: str
    quantity: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: float = field(default_factory=time.time)


class PaperTrader(BrokerBase):
    """Simulated paper trading engine."""

    def __init__(self, initial_capital: float = 100_000):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions: dict[str, PaperPosition] = {}
        self.closed_trades: list[dict] = []
        self.daily_pnl: float = 0.0

    def submit_order(
        self,
        ticker: str,
        direction: str,
        quantity: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> OrderResult:
        price = entry_price or 0.0

        # Check if closing existing position
        if ticker in self.positions:
            pos = self.positions.pop(ticker)
            if pos.direction == "buy":
                pnl = (price - pos.entry_price) * pos.quantity
            else:
                pnl = (pos.entry_price - price) * pos.quantity
            self.capital += pnl
            self.daily_pnl += pnl
            self.closed_trades.append({
                "ticker": ticker,
                "direction": pos.direction,
                "entry_price": pos.entry_price,
                "exit_price": price,
                "quantity": pos.quantity,
                "pnl": pnl,
                "closed_at": time.time(),
            })
            return OrderResult(
                success=True,
                order_id=str(uuid.uuid4())[:8],
                filled_price=price,
                message=f"Closed {ticker} position. P&L: ${pnl:.2f}",
            )

        # Open new position
        cost = price * quantity
        if cost > self.capital:
            return OrderResult(
                success=False,
                message=f"Insufficient capital. Need ${cost:.2f}, have ${self.capital:.2f}",
            )

        self.positions[ticker] = PaperPosition(
            ticker=ticker,
            direction=direction,
            quantity=quantity,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        return OrderResult(
            success=True,
            order_id=str(uuid.uuid4())[:8],
            filled_price=price,
            message=f"Opened {direction.upper()} {quantity} {ticker} @ ${price:.2f}",
        )

    def get_position(self, ticker: str) -> Optional[dict]:
        pos = self.positions.get(ticker)
        if pos is None:
            return None
        return {
            "ticker": pos.ticker,
            "direction": pos.direction,
            "quantity": pos.quantity,
            "entry_price": pos.entry_price,
            "stop_loss": pos.stop_loss,
            "take_profit": pos.take_profit,
        }

    def get_account_value(self) -> float:
        return self.capital

    def get_daily_pnl(self) -> float:
        return self.daily_pnl

    def reset_daily_pnl(self):
        self.daily_pnl = 0.0
