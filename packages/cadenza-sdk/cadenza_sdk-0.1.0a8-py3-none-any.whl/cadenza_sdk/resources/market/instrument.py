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
from ...types.market import instrument_list_params
from ...types.market.instrument_list_response import InstrumentListResponse

__all__ = ["InstrumentResource", "AsyncInstrumentResource"]


class InstrumentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InstrumentResourceWithRawResponse:
        return InstrumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InstrumentResourceWithStreamingResponse:
        return InstrumentResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        detail: bool | NotGiven = NOT_GIVEN,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"]
        | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstrumentListResponse:
        """
        List available exchange symbols

        Args:
          detail: Whether to return detailed information

          exchange_type: Exchange type

          symbol: Symbol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/market/listSymbolInfo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "detail": detail,
                        "exchange_type": exchange_type,
                        "symbol": symbol,
                    },
                    instrument_list_params.InstrumentListParams,
                ),
            ),
            cast_to=InstrumentListResponse,
        )


class AsyncInstrumentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInstrumentResourceWithRawResponse:
        return AsyncInstrumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInstrumentResourceWithStreamingResponse:
        return AsyncInstrumentResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        detail: bool | NotGiven = NOT_GIVEN,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"]
        | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstrumentListResponse:
        """
        List available exchange symbols

        Args:
          detail: Whether to return detailed information

          exchange_type: Exchange type

          symbol: Symbol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/market/listSymbolInfo",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "detail": detail,
                        "exchange_type": exchange_type,
                        "symbol": symbol,
                    },
                    instrument_list_params.InstrumentListParams,
                ),
            ),
            cast_to=InstrumentListResponse,
        )


class InstrumentResourceWithRawResponse:
    def __init__(self, instrument: InstrumentResource) -> None:
        self._instrument = instrument

        self.list = to_raw_response_wrapper(
            instrument.list,
        )


class AsyncInstrumentResourceWithRawResponse:
    def __init__(self, instrument: AsyncInstrumentResource) -> None:
        self._instrument = instrument

        self.list = async_to_raw_response_wrapper(
            instrument.list,
        )


class InstrumentResourceWithStreamingResponse:
    def __init__(self, instrument: InstrumentResource) -> None:
        self._instrument = instrument

        self.list = to_streamed_response_wrapper(
            instrument.list,
        )


class AsyncInstrumentResourceWithStreamingResponse:
    def __init__(self, instrument: AsyncInstrumentResource) -> None:
        self._instrument = instrument

        self.list = async_to_streamed_response_wrapper(
            instrument.list,
        )
