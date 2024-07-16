# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["OrderListParams"]


class OrderListParams(TypedDict, total=False):
    end_time: Annotated[int, PropertyInfo(alias="endTime")]
    """End time (in unix milliseconds)"""

    exchange_account_id: Annotated[str, PropertyInfo(alias="exchangeAccountId")]
    """Exchange account ID"""

    limit: int
    """Limit the number of returned results."""

    offset: int
    """Offset of the returned results. Default: 0"""

    order_id: Annotated[str, PropertyInfo(alias="orderId")]
    """Order ID"""

    order_status: Annotated[
        Literal[
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
        ],
        PropertyInfo(alias="orderStatus"),
    ]
    """Order status"""

    start_time: Annotated[int, PropertyInfo(alias="startTime")]
    """Start time (in unix milliseconds)"""

    symbol: str
    """Symbol"""

    tenant_id: Annotated[str, PropertyInfo(alias="tenantId")]
    """Tenant ID"""
