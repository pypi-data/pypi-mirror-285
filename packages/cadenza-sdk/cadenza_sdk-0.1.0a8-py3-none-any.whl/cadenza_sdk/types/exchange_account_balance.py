# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExchangeAccountBalance", "Balance"]


class Balance(BaseModel):
    asset: str
    """Asset"""

    free: float
    """Free balance"""

    locked: float
    """Locked balance"""

    total: float
    """Total balance"""


class ExchangeAccountBalance(BaseModel):
    balances: List[Balance]
    """List of balances"""

    exchange_account_id: str = FieldInfo(alias="exchangeAccountId")
    """Exchange account ID"""
