# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["QuoteRequestForQuoteParams"]


class QuoteRequestForQuoteParams(TypedDict, total=False):
    base_currency: Required[Annotated[str, PropertyInfo(alias="baseCurrency")]]
    """Base currency is the currency you want to buy or sell"""

    order_side: Required[Annotated[str, PropertyInfo(alias="orderSide")]]
    """Order side, BUY or SELL"""

    quote_currency: Required[Annotated[str, PropertyInfo(alias="quoteCurrency")]]
    """
    Quote currency is the currency you want to pay or receive, and the price of the
    base currency is quoted in the quote currency
    """

    exchange_account_id: Annotated[str, PropertyInfo(alias="exchangeAccountId")]
    """The identifier for the exchange account"""

    quantity: float
    """Amount of the base currency"""

    quote_quantity: Annotated[float, PropertyInfo(alias="quoteQuantity")]
    """Amount of the quote currency"""
