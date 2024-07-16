# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExchangeAccountUpdateParams"]


class ExchangeAccountUpdateParams(TypedDict, total=False):
    exchange_account_id: Required[Annotated[str, PropertyInfo(alias="exchangeAccountId")]]
    """Exchange account ID"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key"""

    api_secret: Annotated[str, PropertyInfo(alias="apiSecret")]
    """API secret"""

    exchange_account_name: Annotated[str, PropertyInfo(alias="exchangeAccountName")]
    """Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)"""
