"""Custom indicator placeholder.

Add your own indicators here following the module contract:

def detect(df: pd.DataFrame, **params) -> pd.DataFrame:
    # Add indicator columns to df and return it.

def get_shapes(df: pd.DataFrame, **params) -> list[dict]:
    # Return Plotly shape/annotation dicts for chart overlays.
"""

import pandas as pd


def detect(df: pd.DataFrame, **params) -> pd.DataFrame:
    """No-op placeholder. Replace with your indicator logic."""
    return df


def get_shapes(df: pd.DataFrame, **params) -> list[dict]:
    """No-op placeholder. Return empty list."""
    return []
