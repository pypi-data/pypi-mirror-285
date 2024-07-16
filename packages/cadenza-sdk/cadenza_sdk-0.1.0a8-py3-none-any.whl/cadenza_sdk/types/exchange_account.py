# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExchangeAccount"]


class ExchangeAccount(BaseModel):
    account_type: Literal["SPOT", "MARGIN"] = FieldInfo(alias="accountType")
    """Type of account (SPOT, MARGIN)"""

    environment: Literal["REAL", "SANDBOX", "PAPER"]
    """Environment of the exchange account"""

    exchange_account_id: str = FieldInfo(alias="exchangeAccountId")
    """Exchange account ID"""

    exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"] = FieldInfo(
        alias="exchangeType"
    )
    """Exchange type"""

    name: str
    """Name of the exchange account"""

    status: Literal["ACTIVE", "API_ERROR", "INVALID_API", "API_ISSUE", "NOT_TRUSTED", "DELETED"]
    """Status of the exchange account"""
