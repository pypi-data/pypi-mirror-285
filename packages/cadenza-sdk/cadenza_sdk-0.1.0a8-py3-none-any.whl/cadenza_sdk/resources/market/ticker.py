# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

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
from ...types.market import ticker_get_params
from ...types.market.ticker_get_response import TickerGetResponse

__all__ = ["TickerResource", "AsyncTickerResource"]


class TickerResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TickerResourceWithRawResponse:
        return TickerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TickerResourceWithStreamingResponse:
        return TickerResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        symbol: str,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TickerGetResponse:
        """
        Symbol price

        Args:
          symbol: Symbol

          exchange_type: Exchange type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "symbol": symbol,
                        "exchange_type": exchange_type,
                    },
                    ticker_get_params.TickerGetParams,
                ),
            ),
            cast_to=TickerGetResponse,
        )


class AsyncTickerResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTickerResourceWithRawResponse:
        return AsyncTickerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTickerResourceWithStreamingResponse:
        return AsyncTickerResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        symbol: str,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TickerGetResponse:
        """
        Symbol price

        Args:
          symbol: Symbol

          exchange_type: Exchange type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "symbol": symbol,
                        "exchange_type": exchange_type,
                    },
                    ticker_get_params.TickerGetParams,
                ),
            ),
            cast_to=TickerGetResponse,
        )


class TickerResourceWithRawResponse:
    def __init__(self, ticker: TickerResource) -> None:
        self._ticker = ticker

        self.get = to_raw_response_wrapper(
            ticker.get,
        )


class AsyncTickerResourceWithRawResponse:
    def __init__(self, ticker: AsyncTickerResource) -> None:
        self._ticker = ticker

        self.get = async_to_raw_response_wrapper(
            ticker.get,
        )


class TickerResourceWithStreamingResponse:
    def __init__(self, ticker: TickerResource) -> None:
        self._ticker = ticker

        self.get = to_streamed_response_wrapper(
            ticker.get,
        )


class AsyncTickerResourceWithStreamingResponse:
    def __init__(self, ticker: AsyncTickerResource) -> None:
        self._ticker = ticker

        self.get = async_to_streamed_response_wrapper(
            ticker.get,
        )
