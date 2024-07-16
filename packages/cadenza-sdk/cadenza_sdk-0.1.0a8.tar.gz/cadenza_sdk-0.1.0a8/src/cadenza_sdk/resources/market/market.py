# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .kline import (
    KlineResource,
    AsyncKlineResource,
    KlineResourceWithRawResponse,
    AsyncKlineResourceWithRawResponse,
    KlineResourceWithStreamingResponse,
    AsyncKlineResourceWithStreamingResponse,
)
from .ticker import (
    TickerResource,
    AsyncTickerResource,
    TickerResourceWithRawResponse,
    AsyncTickerResourceWithRawResponse,
    TickerResourceWithStreamingResponse,
    AsyncTickerResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .orderbook import (
    OrderbookResource,
    AsyncOrderbookResource,
    OrderbookResourceWithRawResponse,
    AsyncOrderbookResourceWithRawResponse,
    OrderbookResourceWithStreamingResponse,
    AsyncOrderbookResourceWithStreamingResponse,
)
from .instrument import (
    InstrumentResource,
    AsyncInstrumentResource,
    InstrumentResourceWithRawResponse,
    AsyncInstrumentResourceWithRawResponse,
    InstrumentResourceWithStreamingResponse,
    AsyncInstrumentResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["MarketResource", "AsyncMarketResource"]


class MarketResource(SyncAPIResource):
    @cached_property
    def instrument(self) -> InstrumentResource:
        return InstrumentResource(self._client)

    @cached_property
    def ticker(self) -> TickerResource:
        return TickerResource(self._client)

    @cached_property
    def orderbook(self) -> OrderbookResource:
        return OrderbookResource(self._client)

    @cached_property
    def kline(self) -> KlineResource:
        return KlineResource(self._client)

    @cached_property
    def with_raw_response(self) -> MarketResourceWithRawResponse:
        return MarketResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MarketResourceWithStreamingResponse:
        return MarketResourceWithStreamingResponse(self)


class AsyncMarketResource(AsyncAPIResource):
    @cached_property
    def instrument(self) -> AsyncInstrumentResource:
        return AsyncInstrumentResource(self._client)

    @cached_property
    def ticker(self) -> AsyncTickerResource:
        return AsyncTickerResource(self._client)

    @cached_property
    def orderbook(self) -> AsyncOrderbookResource:
        return AsyncOrderbookResource(self._client)

    @cached_property
    def kline(self) -> AsyncKlineResource:
        return AsyncKlineResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMarketResourceWithRawResponse:
        return AsyncMarketResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMarketResourceWithStreamingResponse:
        return AsyncMarketResourceWithStreamingResponse(self)


class MarketResourceWithRawResponse:
    def __init__(self, market: MarketResource) -> None:
        self._market = market

    @cached_property
    def instrument(self) -> InstrumentResourceWithRawResponse:
        return InstrumentResourceWithRawResponse(self._market.instrument)

    @cached_property
    def ticker(self) -> TickerResourceWithRawResponse:
        return TickerResourceWithRawResponse(self._market.ticker)

    @cached_property
    def orderbook(self) -> OrderbookResourceWithRawResponse:
        return OrderbookResourceWithRawResponse(self._market.orderbook)

    @cached_property
    def kline(self) -> KlineResourceWithRawResponse:
        return KlineResourceWithRawResponse(self._market.kline)


class AsyncMarketResourceWithRawResponse:
    def __init__(self, market: AsyncMarketResource) -> None:
        self._market = market

    @cached_property
    def instrument(self) -> AsyncInstrumentResourceWithRawResponse:
        return AsyncInstrumentResourceWithRawResponse(self._market.instrument)

    @cached_property
    def ticker(self) -> AsyncTickerResourceWithRawResponse:
        return AsyncTickerResourceWithRawResponse(self._market.ticker)

    @cached_property
    def orderbook(self) -> AsyncOrderbookResourceWithRawResponse:
        return AsyncOrderbookResourceWithRawResponse(self._market.orderbook)

    @cached_property
    def kline(self) -> AsyncKlineResourceWithRawResponse:
        return AsyncKlineResourceWithRawResponse(self._market.kline)


class MarketResourceWithStreamingResponse:
    def __init__(self, market: MarketResource) -> None:
        self._market = market

    @cached_property
    def instrument(self) -> InstrumentResourceWithStreamingResponse:
        return InstrumentResourceWithStreamingResponse(self._market.instrument)

    @cached_property
    def ticker(self) -> TickerResourceWithStreamingResponse:
        return TickerResourceWithStreamingResponse(self._market.ticker)

    @cached_property
    def orderbook(self) -> OrderbookResourceWithStreamingResponse:
        return OrderbookResourceWithStreamingResponse(self._market.orderbook)

    @cached_property
    def kline(self) -> KlineResourceWithStreamingResponse:
        return KlineResourceWithStreamingResponse(self._market.kline)


class AsyncMarketResourceWithStreamingResponse:
    def __init__(self, market: AsyncMarketResource) -> None:
        self._market = market

    @cached_property
    def instrument(self) -> AsyncInstrumentResourceWithStreamingResponse:
        return AsyncInstrumentResourceWithStreamingResponse(self._market.instrument)

    @cached_property
    def ticker(self) -> AsyncTickerResourceWithStreamingResponse:
        return AsyncTickerResourceWithStreamingResponse(self._market.ticker)

    @cached_property
    def orderbook(self) -> AsyncOrderbookResourceWithStreamingResponse:
        return AsyncOrderbookResourceWithStreamingResponse(self._market.orderbook)

    @cached_property
    def kline(self) -> AsyncKlineResourceWithStreamingResponse:
        return AsyncKlineResourceWithStreamingResponse(self._market.kline)
