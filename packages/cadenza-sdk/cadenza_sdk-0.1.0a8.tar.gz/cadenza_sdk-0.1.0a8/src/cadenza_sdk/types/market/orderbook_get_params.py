# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["OrderbookGetParams"]


class OrderbookGetParams(TypedDict, total=False):
    exchange_type: Required[
        Annotated[
            Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
            PropertyInfo(alias="exchangeType"),
        ]
    ]
    """Exchange type"""

    symbol: Required[str]
    """Symbol"""

    limit: int
    """Limit the number of returned results."""
