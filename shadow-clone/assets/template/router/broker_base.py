"""Abstract broker interface. Implement for each broker."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str] = None
    filled_price: Optional[float] = None
    message: str = ""


class BrokerBase(ABC):
    """Base class for all broker integrations."""

    @abstractmethod
    def submit_order(
        self,
        ticker: str,
        direction: str,
        quantity: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> OrderResult:
        """Submit an order to the broker."""
        ...

    @abstractmethod
    def get_position(self, ticker: str) -> Optional[dict]:
        """Get current position for a ticker."""
        ...

    @abstractmethod
    def get_account_value(self) -> float:
        """Get current account/portfolio value."""
        ...
