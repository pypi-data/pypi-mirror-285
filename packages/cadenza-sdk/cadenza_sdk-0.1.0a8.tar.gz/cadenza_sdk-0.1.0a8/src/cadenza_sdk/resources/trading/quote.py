# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.trading import quote_request_for_quote_params
from ...types.trading.quote_request_for_quote_response import QuoteRequestForQuoteResponse

__all__ = ["QuoteResource", "AsyncQuoteResource"]


class QuoteResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QuoteResourceWithRawResponse:
        return QuoteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QuoteResourceWithStreamingResponse:
        return QuoteResourceWithStreamingResponse(self)

    def request_for_quote(
        self,
        *,
        base_currency: str,
        order_side: str,
        quote_currency: str,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        quantity: float | NotGiven = NOT_GIVEN,
        quote_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuoteRequestForQuoteResponse:
        """
        Quote will give the best quote from all available exchange accounts

        Args:
          base_currency: Base currency is the currency you want to buy or sell

          order_side: Order side, BUY or SELL

          quote_currency: Quote currency is the currency you want to pay or receive, and the price of the
              base currency is quoted in the quote currency

          exchange_account_id: The identifier for the exchange account

          quantity: Amount of the base currency

          quote_quantity: Amount of the quote currency

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/trading/fetchQuotes",
            body=maybe_transform(
                {
                    "base_currency": base_currency,
                    "order_side": order_side,
                    "quote_currency": quote_currency,
                    "exchange_account_id": exchange_account_id,
                    "quantity": quantity,
                    "quote_quantity": quote_quantity,
                },
                quote_request_for_quote_params.QuoteRequestForQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuoteRequestForQuoteResponse,
        )


class AsyncQuoteResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQuoteResourceWithRawResponse:
        return AsyncQuoteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQuoteResourceWithStreamingResponse:
        return AsyncQuoteResourceWithStreamingResponse(self)

    async def request_for_quote(
        self,
        *,
        base_currency: str,
        order_side: str,
        quote_currency: str,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        quantity: float | NotGiven = NOT_GIVEN,
        quote_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuoteRequestForQuoteResponse:
        """
        Quote will give the best quote from all available exchange accounts

        Args:
          base_currency: Base currency is the currency you want to buy or sell

          order_side: Order side, BUY or SELL

          quote_currency: Quote currency is the currency you want to pay or receive, and the price of the
              base currency is quoted in the quote currency

          exchange_account_id: The identifier for the exchange account

          quantity: Amount of the base currency

          quote_quantity: Amount of the quote currency

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/trading/fetchQuotes",
            body=await async_maybe_transform(
                {
                    "base_currency": base_currency,
                    "order_side": order_side,
                    "quote_currency": quote_currency,
                    "exchange_account_id": exchange_account_id,
                    "quantity": quantity,
                    "quote_quantity": quote_quantity,
                },
                quote_request_for_quote_params.QuoteRequestForQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuoteRequestForQuoteResponse,
        )


class QuoteResourceWithRawResponse:
    def __init__(self, quote: QuoteResource) -> None:
        self._quote = quote

        self.request_for_quote = to_raw_response_wrapper(
            quote.request_for_quote,
        )


class AsyncQuoteResourceWithRawResponse:
    def __init__(self, quote: AsyncQuoteResource) -> None:
        self._quote = quote

        self.request_for_quote = async_to_raw_response_wrapper(
            quote.request_for_quote,
        )


class QuoteResourceWithStreamingResponse:
    def __init__(self, quote: QuoteResource) -> None:
        self._quote = quote

        self.request_for_quote = to_streamed_response_wrapper(
            quote.request_for_quote,
        )


class AsyncQuoteResourceWithStreamingResponse:
    def __init__(self, quote: AsyncQuoteResource) -> None:
        self._quote = quote

        self.request_for_quote = async_to_streamed_response_wrapper(
            quote.request_for_quote,
        )
