"""Signal parsing engine — extracts structured trade data from natural language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .patterns import ALL_PATTERNS
from .normalizer import normalize_direction, normalize_ticker, normalize_price


@dataclass
class ParsedSignal:
    ticker: str
    direction: str  # 'buy' or 'sell'
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float  # 0.0 - 1.0
    pattern_name: str  # Which pattern matched
    raw_message: str


def parse_signal(message: str) -> Optional[ParsedSignal]:
    """Parse a trading signal from a chat message.

    Tries each pattern in priority order. Returns the first confident match,
    or None if the message doesn't look like a trading signal.
    """
    cleaned = message.strip()
    if not cleaned:
        return None

    for pattern_name, pattern in ALL_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            groups = match.groupdict()

            ticker = normalize_ticker(groups.get("ticker", ""))
            direction = normalize_direction(groups.get("direction", ""))
            entry = normalize_price(groups.get("entry"))
            stop_loss = normalize_price(groups.get("stop_loss"))
            take_profit = normalize_price(groups.get("take_profit"))

            if not ticker or direction not in ("buy", "sell"):
                continue

            # Confidence scoring
            confidence = _score_confidence(ticker, entry, stop_loss, take_profit)

            return ParsedSignal(
                ticker=ticker,
                direction=direction,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                pattern_name=pattern_name,
                raw_message=cleaned,
            )

    return None


def _score_confidence(
    ticker: str,
    entry: Optional[float],
    stop_loss: Optional[float],
    take_profit: Optional[float],
) -> float:
    """Score confidence 0.0 - 1.0 based on how much info was extracted."""
    score = 0.3  # Base: we have ticker + direction

    if entry is not None:
        score += 0.3
    if stop_loss is not None:
        score += 0.2
    if take_profit is not None:
        score += 0.2

    # Bonus: valid ticker length
    if 1 <= len(ticker) <= 5 and ticker.isalpha():
        score = min(score + 0.05, 1.0)

    # Penalty: suspiciously high/low prices
    if entry is not None and (entry <= 0 or entry > 100_000):
        score -= 0.3

    return max(0.0, min(1.0, score))
