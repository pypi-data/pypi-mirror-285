# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["OrderCreateParams"]


class OrderCreateParams(TypedDict, total=False):
    exchange_account_id: Annotated[str, PropertyInfo(alias="exchangeAccountId")]
    """Exchange account ID"""

    leverage: int
    """Levarage"""

    order_side: Annotated[Literal["BUY", "SELL"], PropertyInfo(alias="orderSide")]
    """Order side"""

    order_type: Annotated[
        Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"],
        PropertyInfo(alias="orderType"),
    ]
    """Order type"""

    position_id: Annotated[str, PropertyInfo(alias="positionId")]
    """Position ID for closing position in margin trading"""

    price: float
    """Price"""

    price_slippage_tolerance: Annotated[float, PropertyInfo(alias="priceSlippageTolerance")]
    """Price slippage tolerance, range: [0, 0.1] with 2 decimal places"""

    priority: List[str]
    """Priority list of exchange account ID in descending order"""

    quantity: float
    """Quantity.

    One of quantity or quoteQuantity must be provided. If both is provided, only
    quantity will be used.
    """

    quote_id: Annotated[str, PropertyInfo(alias="quoteId")]
    """Quote ID used by exchange for RFQ, e.g.

    WINTERMUTE need this field to execute QUOTED order
    """

    quote_quantity: Annotated[float, PropertyInfo(alias="quoteQuantity")]
    """Quote Quantity"""

    quote_request_id: Annotated[str, PropertyInfo(alias="quoteRequestId")]
    """Quote request ID"""

    route_policy: Annotated[Literal["PRIORITY", "QUOTE"], PropertyInfo(alias="routePolicy")]
    """Route policy.

    For PRIORITY, the order request will be routed to the exchange account with the
    highest priority. For QUOTE, the system will execute the execution plan based on
    the quote. Order request with route policy QUOTE will only accept two
    parameters, quoteRequestId and priceSlippageTolerance
    """

    symbol: str
    """Symbol"""

    tenant_id: Annotated[str, PropertyInfo(alias="tenantId")]
    """Tenant ID"""

    time_in_force: Annotated[
        Literal["DAY", "GTC", "GTX", "GTD", "OPG", "CLS", "IOC", "FOK", "GFA", "GFS", "GTM", "MOO", "MOC", "EXT"],
        PropertyInfo(alias="timeInForce"),
    ]
    """Time in force"""

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]
