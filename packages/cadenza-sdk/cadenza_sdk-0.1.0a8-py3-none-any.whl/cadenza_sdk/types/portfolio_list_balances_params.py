# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PortfolioListBalancesParams"]


class PortfolioListBalancesParams(TypedDict, total=False):
    exchange_account_id: Annotated[str, PropertyInfo(alias="exchangeAccountId")]
    """Exchange account ID"""

    hide_empty_value: Annotated[bool, PropertyInfo(alias="hideEmptyValue")]
    """Hide small account"""
