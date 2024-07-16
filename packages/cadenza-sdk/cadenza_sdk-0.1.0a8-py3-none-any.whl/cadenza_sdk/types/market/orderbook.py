# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Orderbook"]


class Orderbook(BaseModel):
    asks: Optional[List[List[float]]] = None

    bids: Optional[List[List[float]]] = None

    exchange_type: Optional[str] = FieldInfo(alias="exchangeType", default=None)

    level: Optional[int] = None
    """Order book level"""

    symbol: Optional[str] = None
