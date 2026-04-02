"""Regex pattern library for common trading signal formats.

Each pattern returns named groups: ticker, direction, entry, stop_loss, take_profit.
Add new patterns for specific signal groups.
"""

from __future__ import annotations

import re

# ─── Pattern Definitions ─────────────────────────────────────────────────────

# Format: "BUY NVDA 170.00 SL 168.00 TP 175.00"
STANDARD_FORMAT = re.compile(
    r"(?P<direction>BUY|SELL|LONG|SHORT)\s+"
    r"(?P<ticker>[A-Z]{1,5})\s+"
    r"(?P<entry>[\d]+\.?\d*)"
    r"(?:\s+SL\s+(?P<stop_loss>[\d]+\.?\d*))?"
    r"(?:\s+TP\s+(?P<take_profit>[\d]+\.?\d*))?",
    re.IGNORECASE,
)

# Format: "NVDA 🟢 Buy @ 170.00 | SL: 168.00 | TP: 175.00"
EMOJI_FORMAT = re.compile(
    r"(?P<ticker>[A-Z]{1,5})\s*"
    r"[🟢🔴🟩🟥⬆⬇️↑↓]\s*"
    r"(?P<direction>Buy|Sell|Long|Short)\s*"
    r"[@at]*\s*(?P<entry>[\d]+\.?\d*)"
    r"(?:\s*\|\s*SL[:\s]*(?P<stop_loss>[\d]+\.?\d*))?"
    r"(?:\s*\|\s*TP[:\s]*(?P<take_profit>[\d]+\.?\d*))?",
    re.IGNORECASE,
)

# Format: "🚀 NVDA Entry: 170.00 Stop: 168.00 Target: 175.00"
ALERT_FORMAT = re.compile(
    r"(?P<ticker>[A-Z]{1,5})\s+"
    r"(?:Entry|Price|@)[:\s]*(?P<entry>[\d]+\.?\d*)\s*"
    r"(?:Stop|SL|Stoploss)[:\s]*(?P<stop_loss>[\d]+\.?\d*)\s*"
    r"(?:Target|TP|Take\s*Profit)[:\s]*(?P<take_profit>[\d]+\.?\d*)",
    re.IGNORECASE,
)

# Format: "$NVDA calls 170" or "$NVDA puts 170"
OPTIONS_SHORTHAND = re.compile(
    r"\$(?P<ticker>[A-Z]{1,5})\s+"
    r"(?P<direction>calls?|puts?)\s+"
    r"(?P<entry>[\d]+\.?\d*)",
    re.IGNORECASE,
)

# Format: "Buying NVDA at 170, stop at 168"
CONVERSATIONAL_FORMAT = re.compile(
    r"(?P<direction>Buying|Selling|Going\s+long|Going\s+short|Longing|Shorting)\s+"
    r"(?P<ticker>[A-Z]{1,5})\s+"
    r"(?:at|@)\s*(?P<entry>[\d]+\.?\d*)"
    r"(?:[,\s]+stop\s+(?:at\s+)?(?P<stop_loss>[\d]+\.?\d*))?",
    re.IGNORECASE,
)

# All patterns in priority order
ALL_PATTERNS = [
    ("standard", STANDARD_FORMAT),
    ("emoji", EMOJI_FORMAT),
    ("alert", ALERT_FORMAT),
    ("options", OPTIONS_SHORTHAND),
    ("conversational", CONVERSATIONAL_FORMAT),
]
