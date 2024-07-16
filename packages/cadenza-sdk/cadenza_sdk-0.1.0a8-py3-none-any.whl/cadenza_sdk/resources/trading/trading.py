# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .order import (
    OrderResource,
    AsyncOrderResource,
    OrderResourceWithRawResponse,
    AsyncOrderResourceWithRawResponse,
    OrderResourceWithStreamingResponse,
    AsyncOrderResourceWithStreamingResponse,
)
from .quote import (
    QuoteResource,
    AsyncQuoteResource,
    QuoteResourceWithRawResponse,
    AsyncQuoteResourceWithRawResponse,
    QuoteResourceWithStreamingResponse,
    AsyncQuoteResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .execution_report import (
    ExecutionReportResource,
    AsyncExecutionReportResource,
    ExecutionReportResourceWithRawResponse,
    AsyncExecutionReportResourceWithRawResponse,
    ExecutionReportResourceWithStreamingResponse,
    AsyncExecutionReportResourceWithStreamingResponse,
)

__all__ = ["TradingResource", "AsyncTradingResource"]


class TradingResource(SyncAPIResource):
    @cached_property
    def order(self) -> OrderResource:
        return OrderResource(self._client)

    @cached_property
    def quote(self) -> QuoteResource:
        return QuoteResource(self._client)

    @cached_property
    def execution_report(self) -> ExecutionReportResource:
        return ExecutionReportResource(self._client)

    @cached_property
    def with_raw_response(self) -> TradingResourceWithRawResponse:
        return TradingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TradingResourceWithStreamingResponse:
        return TradingResourceWithStreamingResponse(self)


class AsyncTradingResource(AsyncAPIResource):
    @cached_property
    def order(self) -> AsyncOrderResource:
        return AsyncOrderResource(self._client)

    @cached_property
    def quote(self) -> AsyncQuoteResource:
        return AsyncQuoteResource(self._client)

    @cached_property
    def execution_report(self) -> AsyncExecutionReportResource:
        return AsyncExecutionReportResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTradingResourceWithRawResponse:
        return AsyncTradingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTradingResourceWithStreamingResponse:
        return AsyncTradingResourceWithStreamingResponse(self)


class TradingResourceWithRawResponse:
    def __init__(self, trading: TradingResource) -> None:
        self._trading = trading

    @cached_property
    def order(self) -> OrderResourceWithRawResponse:
        return OrderResourceWithRawResponse(self._trading.order)

    @cached_property
    def quote(self) -> QuoteResourceWithRawResponse:
        return QuoteResourceWithRawResponse(self._trading.quote)

    @cached_property
    def execution_report(self) -> ExecutionReportResourceWithRawResponse:
        return ExecutionReportResourceWithRawResponse(self._trading.execution_report)


class AsyncTradingResourceWithRawResponse:
    def __init__(self, trading: AsyncTradingResource) -> None:
        self._trading = trading

    @cached_property
    def order(self) -> AsyncOrderResourceWithRawResponse:
        return AsyncOrderResourceWithRawResponse(self._trading.order)

    @cached_property
    def quote(self) -> AsyncQuoteResourceWithRawResponse:
        return AsyncQuoteResourceWithRawResponse(self._trading.quote)

    @cached_property
    def execution_report(self) -> AsyncExecutionReportResourceWithRawResponse:
        return AsyncExecutionReportResourceWithRawResponse(self._trading.execution_report)


class TradingResourceWithStreamingResponse:
    def __init__(self, trading: TradingResource) -> None:
        self._trading = trading

    @cached_property
    def order(self) -> OrderResourceWithStreamingResponse:
        return OrderResourceWithStreamingResponse(self._trading.order)

    @cached_property
    def quote(self) -> QuoteResourceWithStreamingResponse:
        return QuoteResourceWithStreamingResponse(self._trading.quote)

    @cached_property
    def execution_report(self) -> ExecutionReportResourceWithStreamingResponse:
        return ExecutionReportResourceWithStreamingResponse(self._trading.execution_report)


class AsyncTradingResourceWithStreamingResponse:
    def __init__(self, trading: AsyncTradingResource) -> None:
        self._trading = trading

    @cached_property
    def order(self) -> AsyncOrderResourceWithStreamingResponse:
        return AsyncOrderResourceWithStreamingResponse(self._trading.order)

    @cached_property
    def quote(self) -> AsyncQuoteResourceWithStreamingResponse:
        return AsyncQuoteResourceWithStreamingResponse(self._trading.quote)

    @cached_property
    def execution_report(self) -> AsyncExecutionReportResourceWithStreamingResponse:
        return AsyncExecutionReportResourceWithStreamingResponse(self._trading.execution_report)
