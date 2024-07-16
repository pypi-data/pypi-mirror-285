# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExchangeAccountPosition", "Position"]


class Position(BaseModel):
    amount: float
    """Amount"""

    position_side: Literal["LONG", "SHORT"] = FieldInfo(alias="positionSide")
    """Position side"""

    status: Literal["OPEN"]
    """Status"""

    symbol: str
    """Symbol"""

    cost: Optional[float] = None
    """Cost"""

    entry_price: Optional[float] = FieldInfo(alias="entryPrice", default=None)
    """Entry price"""


class ExchangeAccountPosition(BaseModel):
    exchange_account_id: Optional[str] = FieldInfo(alias="exchangeAccountId", default=None)
    """Exchange account ID"""

    positions: Optional[List[Position]] = None
    """List of positions"""
