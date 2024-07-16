# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Ticker"]


class Ticker(BaseModel):
    exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"] = FieldInfo(
        alias="exchangeType"
    )
    """Exchange type"""

    symbol: str
    """Symbol"""

    timestamp: int
    """Unix timestamp in milliseconds"""

    ask_price: Optional[float] = FieldInfo(alias="askPrice", default=None)
    """Ask price"""

    ask_quantity: Optional[float] = FieldInfo(alias="askQuantity", default=None)
    """Ask quantity"""

    bid_price: Optional[float] = FieldInfo(alias="bidPrice", default=None)
    """Bid price"""

    bid_quantity: Optional[float] = FieldInfo(alias="bidQuantity", default=None)
    """Bid quantity"""

    last_price: Optional[float] = FieldInfo(alias="lastPrice", default=None)
    """Last price"""

    last_quantity: Optional[float] = FieldInfo(alias="lastQuantity", default=None)
    """Last quantity"""
