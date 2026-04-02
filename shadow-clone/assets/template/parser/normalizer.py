"""Normalize parsed signal fields into canonical form."""

from __future__ import annotations

# Direction aliases
_BUY_ALIASES = {"buy", "long", "going long", "longing", "buying", "calls", "call"}
_SELL_ALIASES = {"sell", "short", "going short", "shorting", "selling", "puts", "put"}


def normalize_direction(raw: str) -> str:
    """Normalize direction to 'buy' or 'sell'."""
    cleaned = raw.strip().lower()
    if cleaned in _BUY_ALIASES:
        return "buy"
    if cleaned in _SELL_ALIASES:
        return "sell"
    return cleaned


def normalize_ticker(raw: str) -> str:
    """Normalize ticker to uppercase, strip $ prefix."""
    return raw.strip().upper().lstrip("$")


def normalize_price(raw: str | None) -> float | None:
    """Parse price string to float, return None if invalid."""
    if raw is None:
        return None
    try:
        return float(raw.strip().replace(",", ""))
    except (ValueError, AttributeError):
        return None
