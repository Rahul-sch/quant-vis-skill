"""Alpaca broker integration. Requires API keys in .env."""

from __future__ import annotations

from typing import Optional
import httpx

from .broker_base import BrokerBase, OrderResult
from config import config


class AlpacaRouter(BrokerBase):
    """Route orders to Alpaca paper/live trading API."""

    def __init__(self):
        self.base_url = config.ALPACA_BASE_URL
        self.headers = {
            "APCA-API-KEY-ID": config.ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": config.ALPACA_SECRET_KEY,
        }

    def submit_order(
        self,
        ticker: str,
        direction: str,
        quantity: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> OrderResult:
        side = "buy" if direction == "buy" else "sell"
        order_type = "limit" if entry_price else "market"

        payload = {
            "symbol": ticker,
            "qty": str(int(quantity)),
            "side": side,
            "type": order_type,
            "time_in_force": "day",
        }
        if entry_price:
            payload["limit_price"] = str(entry_price)

        # Bracket order with SL/TP
        if stop_loss and take_profit:
            payload["order_class"] = "bracket"
            payload["stop_loss"] = {"stop_price": str(stop_loss)}
            payload["take_profit"] = {"limit_price": str(take_profit)}
        elif stop_loss:
            payload["order_class"] = "oto"
            payload["stop_loss"] = {"stop_price": str(stop_loss)}

        try:
            resp = httpx.post(
                f"{self.base_url}/v2/orders",
                json=payload,
                headers=self.headers,
                timeout=10,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return OrderResult(
                    success=True,
                    order_id=data.get("id", ""),
                    filled_price=entry_price,
                    message=f"Alpaca order submitted: {data.get('id', '')}",
                )
            else:
                return OrderResult(
                    success=False,
                    message=f"Alpaca error {resp.status_code}: {resp.text}",
                )
        except Exception as e:
            return OrderResult(success=False, message=f"Alpaca request failed: {e}")

    def get_position(self, ticker: str) -> Optional[dict]:
        try:
            resp = httpx.get(
                f"{self.base_url}/v2/positions/{ticker}",
                headers=self.headers,
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def get_account_value(self) -> float:
        try:
            resp = httpx.get(
                f"{self.base_url}/v2/account",
                headers=self.headers,
                timeout=10,
            )
            if resp.status_code == 200:
                return float(resp.json().get("portfolio_value", 0))
            return 0.0
        except Exception:
            return 0.0
