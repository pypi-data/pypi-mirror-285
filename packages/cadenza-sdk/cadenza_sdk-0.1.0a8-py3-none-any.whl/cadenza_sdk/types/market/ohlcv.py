# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Ohlcv"]


class Ohlcv(BaseModel):
    c: Optional[float] = None
    """Close price"""

    h: Optional[float] = None
    """High price"""

    l: Optional[float] = None
    """Low price"""

    o: Optional[float] = None
    """Open price"""

    t: Optional[int] = None
    """Start time (in unix milliseconds)"""

    v: Optional[float] = None
    """Volume"""
