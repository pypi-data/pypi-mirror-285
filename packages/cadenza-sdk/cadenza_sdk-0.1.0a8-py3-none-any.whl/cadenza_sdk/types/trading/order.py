# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Order"]


class Order(BaseModel):
    cost: float
    """The total cost of this order."""

    created_at: int = FieldInfo(alias="createdAt")
    """Created timestamp"""

    exchange_account_id: str = FieldInfo(alias="exchangeAccountId")
    """Exchange account ID"""

    exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"] = FieldInfo(
        alias="exchangeType"
    )
    """Exchange type"""

    filled: float
    """The quantity of this order that has been filled."""

    order_side: Literal["BUY", "SELL"] = FieldInfo(alias="orderSide")
    """Order side"""

    order_type: Literal[
        "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"
    ] = FieldInfo(alias="orderType")
    """Order type"""

    quantity: float
    """Quantity"""

    status: Literal[
        "SUBMITTED",
        "ACCEPTED",
        "OPEN",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "PENDING_CANCEL",
        "REJECTED",
        "EXPIRED",
        "REVOKED",
    ]
    """Order status"""

    symbol: str
    """Symbol"""

    time_in_force: Literal[
        "DAY", "GTC", "GTX", "GTD", "OPG", "CLS", "IOC", "FOK", "GFA", "GFS", "GTM", "MOO", "MOC", "EXT"
    ] = FieldInfo(alias="timeInForce")
    """Time in force"""

    updated_at: int = FieldInfo(alias="updatedAt")
    """Last updated timestamp"""

    fee: Optional[float] = None
    """Fee"""

    fee_currency: Optional[str] = FieldInfo(alias="feeCurrency", default=None)
    """Fee currency"""

    order_id: Optional[str] = FieldInfo(alias="orderId", default=None)

    position_id: Optional[str] = FieldInfo(alias="positionId", default=None)
    """Position ID"""

    price: Optional[float] = None
    """Price"""

    quote_quantity: Optional[float] = FieldInfo(alias="quoteQuantity", default=None)
    """Quote Quantity"""

    tenant_id: Optional[str] = FieldInfo(alias="tenantId", default=None)
    """Tenant ID"""

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)
    """User ID"""
