# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TickerGetParams"]


class TickerGetParams(TypedDict, total=False):
    symbol: Required[str]
    """Symbol"""

    exchange_type: Annotated[
        Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        PropertyInfo(alias="exchangeType"),
    ]
    """Exchange type"""
