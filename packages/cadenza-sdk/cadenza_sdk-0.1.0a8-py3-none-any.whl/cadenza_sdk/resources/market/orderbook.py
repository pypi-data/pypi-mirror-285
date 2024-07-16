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
from ...types.market import orderbook_get_params
from ...types.market.orderbook_get_response import OrderbookGetResponse

__all__ = ["OrderbookResource", "AsyncOrderbookResource"]


class OrderbookResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrderbookResourceWithRawResponse:
        return OrderbookResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrderbookResourceWithStreamingResponse:
        return OrderbookResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        symbol: str,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderbookGetResponse:
        """
        Get order book

        Args:
          exchange_type: Exchange type

          symbol: Symbol

          limit: Limit the number of returned results.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/market/orderbook",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exchange_type": exchange_type,
                        "symbol": symbol,
                        "limit": limit,
                    },
                    orderbook_get_params.OrderbookGetParams,
                ),
            ),
            cast_to=OrderbookGetResponse,
        )


class AsyncOrderbookResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrderbookResourceWithRawResponse:
        return AsyncOrderbookResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrderbookResourceWithStreamingResponse:
        return AsyncOrderbookResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        symbol: str,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderbookGetResponse:
        """
        Get order book

        Args:
          exchange_type: Exchange type

          symbol: Symbol

          limit: Limit the number of returned results.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/market/orderbook",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exchange_type": exchange_type,
                        "symbol": symbol,
                        "limit": limit,
                    },
                    orderbook_get_params.OrderbookGetParams,
                ),
            ),
            cast_to=OrderbookGetResponse,
        )


class OrderbookResourceWithRawResponse:
    def __init__(self, orderbook: OrderbookResource) -> None:
        self._orderbook = orderbook

        self.get = to_raw_response_wrapper(
            orderbook.get,
        )


class AsyncOrderbookResourceWithRawResponse:
    def __init__(self, orderbook: AsyncOrderbookResource) -> None:
        self._orderbook = orderbook

        self.get = async_to_raw_response_wrapper(
            orderbook.get,
        )


class OrderbookResourceWithStreamingResponse:
    def __init__(self, orderbook: OrderbookResource) -> None:
        self._orderbook = orderbook

        self.get = to_streamed_response_wrapper(
            orderbook.get,
        )


class AsyncOrderbookResourceWithStreamingResponse:
    def __init__(self, orderbook: AsyncOrderbookResource) -> None:
        self._orderbook = orderbook

        self.get = async_to_streamed_response_wrapper(
            orderbook.get,
        )
