# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    strip_not_given,
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
from ...pagination import SyncOffset, AsyncOffset
from ..._base_client import AsyncPaginator, make_request_options
from ...types.trading import order_list_params, order_cancel_params, order_create_params
from ...types.trading.order import Order
from ...types.trading.order_create_response import OrderCreateResponse

__all__ = ["OrderResource", "AsyncOrderResource"]


class OrderResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrderResourceWithRawResponse:
        return OrderResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrderResourceWithStreamingResponse:
        return OrderResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        leverage: int | NotGiven = NOT_GIVEN,
        order_side: Literal["BUY", "SELL"] | NotGiven = NOT_GIVEN,
        order_type: Literal[
            "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"
        ]
        | NotGiven = NOT_GIVEN,
        position_id: str | NotGiven = NOT_GIVEN,
        price: float | NotGiven = NOT_GIVEN,
        price_slippage_tolerance: float | NotGiven = NOT_GIVEN,
        priority: List[str] | NotGiven = NOT_GIVEN,
        quantity: float | NotGiven = NOT_GIVEN,
        quote_id: str | NotGiven = NOT_GIVEN,
        quote_quantity: float | NotGiven = NOT_GIVEN,
        quote_request_id: str | NotGiven = NOT_GIVEN,
        route_policy: Literal["PRIORITY", "QUOTE"] | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        tenant_id: str | NotGiven = NOT_GIVEN,
        time_in_force: Literal[
            "DAY", "GTC", "GTX", "GTD", "OPG", "CLS", "IOC", "FOK", "GFA", "GFS", "GTM", "MOO", "MOC", "EXT"
        ]
        | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderCreateResponse:
        """
        Place order

        Args:
          exchange_account_id: Exchange account ID

          leverage: Levarage

          order_side: Order side

          order_type: Order type

          position_id: Position ID for closing position in margin trading

          price: Price

          price_slippage_tolerance: Price slippage tolerance, range: [0, 0.1] with 2 decimal places

          priority: Priority list of exchange account ID in descending order

          quantity: Quantity. One of quantity or quoteQuantity must be provided. If both is
              provided, only quantity will be used.

          quote_id: Quote ID used by exchange for RFQ, e.g. WINTERMUTE need this field to execute
              QUOTED order

          quote_quantity: Quote Quantity

          quote_request_id: Quote request ID

          route_policy: Route policy. For PRIORITY, the order request will be routed to the exchange
              account with the highest priority. For QUOTE, the system will execute the
              execution plan based on the quote. Order request with route policy QUOTE will
              only accept two parameters, quoteRequestId and priceSlippageTolerance

          symbol: Symbol

          tenant_id: Tenant ID

          time_in_force: Time in force

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        return self._post(
            "/api/v2/trading/placeOrder",
            body=maybe_transform(
                {
                    "exchange_account_id": exchange_account_id,
                    "leverage": leverage,
                    "order_side": order_side,
                    "order_type": order_type,
                    "position_id": position_id,
                    "price": price,
                    "price_slippage_tolerance": price_slippage_tolerance,
                    "priority": priority,
                    "quantity": quantity,
                    "quote_id": quote_id,
                    "quote_quantity": quote_quantity,
                    "quote_request_id": quote_request_id,
                    "route_policy": route_policy,
                    "symbol": symbol,
                    "tenant_id": tenant_id,
                    "time_in_force": time_in_force,
                },
                order_create_params.OrderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderCreateResponse,
        )

    def list(
        self,
        *,
        end_time: int | NotGiven = NOT_GIVEN,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order_id: str | NotGiven = NOT_GIVEN,
        order_status: Literal[
            "SUBMITTED",
            "ACCEPTED",
            "OPEN",
            "PARTIALLY_FILLED",
            "FILLED",
            "CANCELED",
            "PENDING_CANCEL",
            "REJECTED",
            "EXPIRED",
            "REVOKED",
        ]
        | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        tenant_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncOffset[Order]:
        """
        List orders

        Args:
          end_time: End time (in unix milliseconds)

          exchange_account_id: Exchange account ID

          limit: Limit the number of returned results.

          offset: Offset of the returned results. Default: 0

          order_id: Order ID

          order_status: Order status

          start_time: Start time (in unix milliseconds)

          symbol: Symbol

          tenant_id: Tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/v2/trading/listOrders",
            page=SyncOffset[Order],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_time": end_time,
                        "exchange_account_id": exchange_account_id,
                        "limit": limit,
                        "offset": offset,
                        "order_id": order_id,
                        "order_status": order_status,
                        "start_time": start_time,
                        "symbol": symbol,
                        "tenant_id": tenant_id,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            model=Order,
        )

    def cancel(
        self,
        *,
        order_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel order.

        If the order is already filled, it will return an error.

        Args:
          order_id: Order ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/trading/cancelOrder",
            body=maybe_transform({"order_id": order_id}, order_cancel_params.OrderCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )


class AsyncOrderResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrderResourceWithRawResponse:
        return AsyncOrderResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrderResourceWithStreamingResponse:
        return AsyncOrderResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        leverage: int | NotGiven = NOT_GIVEN,
        order_side: Literal["BUY", "SELL"] | NotGiven = NOT_GIVEN,
        order_type: Literal[
            "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"
        ]
        | NotGiven = NOT_GIVEN,
        position_id: str | NotGiven = NOT_GIVEN,
        price: float | NotGiven = NOT_GIVEN,
        price_slippage_tolerance: float | NotGiven = NOT_GIVEN,
        priority: List[str] | NotGiven = NOT_GIVEN,
        quantity: float | NotGiven = NOT_GIVEN,
        quote_id: str | NotGiven = NOT_GIVEN,
        quote_quantity: float | NotGiven = NOT_GIVEN,
        quote_request_id: str | NotGiven = NOT_GIVEN,
        route_policy: Literal["PRIORITY", "QUOTE"] | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        tenant_id: str | NotGiven = NOT_GIVEN,
        time_in_force: Literal[
            "DAY", "GTC", "GTX", "GTD", "OPG", "CLS", "IOC", "FOK", "GFA", "GFS", "GTM", "MOO", "MOC", "EXT"
        ]
        | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderCreateResponse:
        """
        Place order

        Args:
          exchange_account_id: Exchange account ID

          leverage: Levarage

          order_side: Order side

          order_type: Order type

          position_id: Position ID for closing position in margin trading

          price: Price

          price_slippage_tolerance: Price slippage tolerance, range: [0, 0.1] with 2 decimal places

          priority: Priority list of exchange account ID in descending order

          quantity: Quantity. One of quantity or quoteQuantity must be provided. If both is
              provided, only quantity will be used.

          quote_id: Quote ID used by exchange for RFQ, e.g. WINTERMUTE need this field to execute
              QUOTED order

          quote_quantity: Quote Quantity

          quote_request_id: Quote request ID

          route_policy: Route policy. For PRIORITY, the order request will be routed to the exchange
              account with the highest priority. For QUOTE, the system will execute the
              execution plan based on the quote. Order request with route policy QUOTE will
              only accept two parameters, quoteRequestId and priceSlippageTolerance

          symbol: Symbol

          tenant_id: Tenant ID

          time_in_force: Time in force

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        return await self._post(
            "/api/v2/trading/placeOrder",
            body=await async_maybe_transform(
                {
                    "exchange_account_id": exchange_account_id,
                    "leverage": leverage,
                    "order_side": order_side,
                    "order_type": order_type,
                    "position_id": position_id,
                    "price": price,
                    "price_slippage_tolerance": price_slippage_tolerance,
                    "priority": priority,
                    "quantity": quantity,
                    "quote_id": quote_id,
                    "quote_quantity": quote_quantity,
                    "quote_request_id": quote_request_id,
                    "route_policy": route_policy,
                    "symbol": symbol,
                    "tenant_id": tenant_id,
                    "time_in_force": time_in_force,
                },
                order_create_params.OrderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderCreateResponse,
        )

    def list(
        self,
        *,
        end_time: int | NotGiven = NOT_GIVEN,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order_id: str | NotGiven = NOT_GIVEN,
        order_status: Literal[
            "SUBMITTED",
            "ACCEPTED",
            "OPEN",
            "PARTIALLY_FILLED",
            "FILLED",
            "CANCELED",
            "PENDING_CANCEL",
            "REJECTED",
            "EXPIRED",
            "REVOKED",
        ]
        | NotGiven = NOT_GIVEN,
        start_time: int | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        tenant_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Order, AsyncOffset[Order]]:
        """
        List orders

        Args:
          end_time: End time (in unix milliseconds)

          exchange_account_id: Exchange account ID

          limit: Limit the number of returned results.

          offset: Offset of the returned results. Default: 0

          order_id: Order ID

          order_status: Order status

          start_time: Start time (in unix milliseconds)

          symbol: Symbol

          tenant_id: Tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/v2/trading/listOrders",
            page=AsyncOffset[Order],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_time": end_time,
                        "exchange_account_id": exchange_account_id,
                        "limit": limit,
                        "offset": offset,
                        "order_id": order_id,
                        "order_status": order_status,
                        "start_time": start_time,
                        "symbol": symbol,
                        "tenant_id": tenant_id,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            model=Order,
        )

    async def cancel(
        self,
        *,
        order_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel order.

        If the order is already filled, it will return an error.

        Args:
          order_id: Order ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/trading/cancelOrder",
            body=await async_maybe_transform({"order_id": order_id}, order_cancel_params.OrderCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )


class OrderResourceWithRawResponse:
    def __init__(self, order: OrderResource) -> None:
        self._order = order

        self.create = to_raw_response_wrapper(
            order.create,
        )
        self.list = to_raw_response_wrapper(
            order.list,
        )
        self.cancel = to_raw_response_wrapper(
            order.cancel,
        )


class AsyncOrderResourceWithRawResponse:
    def __init__(self, order: AsyncOrderResource) -> None:
        self._order = order

        self.create = async_to_raw_response_wrapper(
            order.create,
        )
        self.list = async_to_raw_response_wrapper(
            order.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            order.cancel,
        )


class OrderResourceWithStreamingResponse:
    def __init__(self, order: OrderResource) -> None:
        self._order = order

        self.create = to_streamed_response_wrapper(
            order.create,
        )
        self.list = to_streamed_response_wrapper(
            order.list,
        )
        self.cancel = to_streamed_response_wrapper(
            order.cancel,
        )


class AsyncOrderResourceWithStreamingResponse:
    def __init__(self, order: AsyncOrderResource) -> None:
        self._order = order

        self.create = async_to_streamed_response_wrapper(
            order.create,
        )
        self.list = async_to_streamed_response_wrapper(
            order.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            order.cancel,
        )
