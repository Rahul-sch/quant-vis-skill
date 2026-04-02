"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "paper")

    # Alpaca
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    # Risk controls
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "1000"))
    DAILY_LOSS_LIMIT: float = float(os.getenv("DAILY_LOSS_LIMIT", "500"))
    COOLDOWN_SECONDS: int = int(os.getenv("COOLDOWN_SECONDS", "30"))
    DUPLICATE_WINDOW_SECONDS: int = int(os.getenv("DUPLICATE_WINDOW_SECONDS", "60"))

    # Security
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

    # Allowed tickers
    ALLOWED_TICKERS: list[str] = [
        t.strip().upper()
        for t in os.getenv("ALLOWED_TICKERS", "").split(",")
        if t.strip()
    ]


config = Config()
