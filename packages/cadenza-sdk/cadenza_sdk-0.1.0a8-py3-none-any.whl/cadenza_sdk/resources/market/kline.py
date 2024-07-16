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
from ...types.market import kline_get_params
from ...types.market.kline_get_response import KlineGetResponse

__all__ = ["KlineResource", "AsyncKlineResource"]


class KlineResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KlineResourceWithRawResponse:
        return KlineResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KlineResourceWithStreamingResponse:
        return KlineResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        interval: Literal["1s", "1m", "5m", "15m", "30m", "1h", "2h", "1d", "1w"],
        symbol: str,
        end_time: int | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KlineGetResponse:
        """
        Get historical kline data

        Args:
          exchange_type: Exchange type

          interval: Kline interval

          symbol: Symbol

          end_time: End time (in unix milliseconds)

          limit: Limit the number of returned results.

          start_time: Start time (in unix milliseconds)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/market/kline",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exchange_type": exchange_type,
                        "interval": interval,
                        "symbol": symbol,
                        "end_time": end_time,
                        "limit": limit,
                        "start_time": start_time,
                    },
                    kline_get_params.KlineGetParams,
                ),
            ),
            cast_to=KlineGetResponse,
        )


class AsyncKlineResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKlineResourceWithRawResponse:
        return AsyncKlineResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKlineResourceWithStreamingResponse:
        return AsyncKlineResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        interval: Literal["1s", "1m", "5m", "15m", "30m", "1h", "2h", "1d", "1w"],
        symbol: str,
        end_time: int | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KlineGetResponse:
        """
        Get historical kline data

        Args:
          exchange_type: Exchange type

          interval: Kline interval

          symbol: Symbol

          end_time: End time (in unix milliseconds)

          limit: Limit the number of returned results.

          start_time: Start time (in unix milliseconds)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/market/kline",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exchange_type": exchange_type,
                        "interval": interval,
                        "symbol": symbol,
                        "end_time": end_time,
                        "limit": limit,
                        "start_time": start_time,
                    },
                    kline_get_params.KlineGetParams,
                ),
            ),
            cast_to=KlineGetResponse,
        )


class KlineResourceWithRawResponse:
    def __init__(self, kline: KlineResource) -> None:
        self._kline = kline

        self.get = to_raw_response_wrapper(
            kline.get,
        )


class AsyncKlineResourceWithRawResponse:
    def __init__(self, kline: AsyncKlineResource) -> None:
        self._kline = kline

        self.get = async_to_raw_response_wrapper(
            kline.get,
        )


class KlineResourceWithStreamingResponse:
    def __init__(self, kline: KlineResource) -> None:
        self._kline = kline

        self.get = to_streamed_response_wrapper(
            kline.get,
        )


class AsyncKlineResourceWithStreamingResponse:
    def __init__(self, kline: AsyncKlineResource) -> None:
        self._kline = kline

        self.get = async_to_streamed_response_wrapper(
            kline.get,
        )
