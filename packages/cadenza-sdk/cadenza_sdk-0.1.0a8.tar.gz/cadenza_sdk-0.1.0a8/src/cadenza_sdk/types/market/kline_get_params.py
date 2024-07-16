# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["KlineGetParams"]


class KlineGetParams(TypedDict, total=False):
    exchange_type: Required[
        Annotated[
            Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
            PropertyInfo(alias="exchangeType"),
        ]
    ]
    """Exchange type"""

    interval: Required[Literal["1s", "1m", "5m", "15m", "30m", "1h", "2h", "1d", "1w"]]
    """Kline interval"""

    symbol: Required[str]
    """Symbol"""

    end_time: Annotated[int, PropertyInfo(alias="endTime")]
    """End time (in unix milliseconds)"""

    limit: int
    """Limit the number of returned results."""

    start_time: Annotated[int, PropertyInfo(alias="startTime")]
    """Start time (in unix milliseconds)"""
