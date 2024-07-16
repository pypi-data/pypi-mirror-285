# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExchangeAccountCreateParams"]


class ExchangeAccountCreateParams(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]
    """API key"""

    api_secret: Required[Annotated[str, PropertyInfo(alias="apiSecret")]]
    """API secret"""

    environment: Required[Literal[0, 1]]
    """Environment(0 - real, 1 - sandbox)"""

    exchange_account_name: Required[Annotated[str, PropertyInfo(alias="exchangeAccountName")]]
    """Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)"""

    exchange_type: Required[
        Annotated[
            Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
            PropertyInfo(alias="exchangeType"),
        ]
    ]
    """Exchange type"""
