# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["QuoteWithOrderCandidates", "OrderCandidate"]


class OrderCandidate(BaseModel):
    exchange_account_id: Optional[str] = FieldInfo(alias="exchangeAccountId", default=None)
    """Exchange account ID"""

    order_side: Optional[Literal["BUY", "SELL"]] = FieldInfo(alias="orderSide", default=None)
    """Order side"""

    order_type: Optional[
        Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"]
    ] = FieldInfo(alias="orderType", default=None)
    """Order type"""

    quantity: Optional[float] = None
    """Quantity"""

    quote_quantity: Optional[float] = FieldInfo(alias="quoteQuantity", default=None)
    """Quote Quantity"""

    quote_request_id: Optional[str] = FieldInfo(alias="quoteRequestId", default=None)
    """Quote request ID"""

    route_policy: Optional[Literal["PRIORITY", "QUOTE"]] = FieldInfo(alias="routePolicy", default=None)
    """Route policy.

    For PRIORITY, the order request will be routed to the exchange account with the
    highest priority. For QUOTE, the system will execute the execution plan based on
    the quote. Order request with route policy QUOTE will only accept two
    parameters, quoteRequestId and priceSlippageTolerance
    """

    symbol: Optional[str] = None
    """Symbol"""


class QuoteWithOrderCandidates(BaseModel):
    base_currency: str = FieldInfo(alias="baseCurrency")
    """Base currency"""

    quote_currency: str = FieldInfo(alias="quoteCurrency")
    """Quote currency"""

    quote_request_id: str = FieldInfo(alias="quoteRequestId")
    """Quote request ID"""

    timestamp: int
    """Create time of the quote"""

    valid_until: int = FieldInfo(alias="validUntil")
    """Expiration time of the quote"""

    ask_price: Optional[float] = FieldInfo(alias="askPrice", default=None)
    """Ask price"""

    ask_quantity: Optional[float] = FieldInfo(alias="askQuantity", default=None)
    """Ask quantity"""

    bid_price: Optional[float] = FieldInfo(alias="bidPrice", default=None)
    """Bid price"""

    bid_quantity: Optional[float] = FieldInfo(alias="bidQuantity", default=None)
    """Bid quantity"""

    order_candidates: Optional[List[OrderCandidate]] = FieldInfo(alias="orderCandidates", default=None)
