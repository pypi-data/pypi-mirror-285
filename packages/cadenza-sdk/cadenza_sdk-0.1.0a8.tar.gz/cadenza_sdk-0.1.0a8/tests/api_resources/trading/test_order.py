# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.pagination import SyncOffset, AsyncOffset
from cadenza_sdk.types.trading import (
    Order,
    OrderCreateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrder:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Cadenza) -> None:
        order = client.trading.order.create()
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Cadenza) -> None:
        order = client.trading.order.create(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            leverage=0,
            order_side="BUY",
            order_type="MARKET",
            position_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            price=0,
            price_slippage_tolerance=0,
            priority=["exchange_account_id_1", "exchange_account_id_2", "exchange_account_id_3"],
            quantity=0,
            quote_id="quoteId",
            quote_quantity=0,
            quote_request_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            route_policy="PRIORITY",
            symbol="BTC/USDT",
            tenant_id="tenantId",
            time_in_force="DAY",
            idempotency_key="my_idempotency_key",
        )
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Cadenza) -> None:
        response = client.trading.order.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = response.parse()
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Cadenza) -> None:
        with client.trading.order.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = response.parse()
            assert_matches_type(OrderCreateResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Cadenza) -> None:
        order = client.trading.order.list()
        assert_matches_type(SyncOffset[Order], order, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Cadenza) -> None:
        order = client.trading.order.list(
            end_time=1632933600000,
            exchange_account_id="exchangeAccountId",
            limit=100,
            offset=0,
            order_id="orderId",
            order_status="SUBMITTED",
            start_time=1622505600000,
            symbol="symbol",
            tenant_id="tenantId",
        )
        assert_matches_type(SyncOffset[Order], order, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Cadenza) -> None:
        response = client.trading.order.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = response.parse()
        assert_matches_type(SyncOffset[Order], order, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Cadenza) -> None:
        with client.trading.order.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = response.parse()
            assert_matches_type(SyncOffset[Order], order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: Cadenza) -> None:
        order = client.trading.order.cancel(
            order_id="orderId",
        )
        assert_matches_type(Order, order, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Cadenza) -> None:
        response = client.trading.order.with_raw_response.cancel(
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = response.parse()
        assert_matches_type(Order, order, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Cadenza) -> None:
        with client.trading.order.with_streaming_response.cancel(
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = response.parse()
            assert_matches_type(Order, order, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOrder:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncCadenza) -> None:
        order = await async_client.trading.order.create()
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncCadenza) -> None:
        order = await async_client.trading.order.create(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            leverage=0,
            order_side="BUY",
            order_type="MARKET",
            position_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            price=0,
            price_slippage_tolerance=0,
            priority=["exchange_account_id_1", "exchange_account_id_2", "exchange_account_id_3"],
            quantity=0,
            quote_id="quoteId",
            quote_quantity=0,
            quote_request_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            route_policy="PRIORITY",
            symbol="BTC/USDT",
            tenant_id="tenantId",
            time_in_force="DAY",
            idempotency_key="my_idempotency_key",
        )
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.order.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = await response.parse()
        assert_matches_type(OrderCreateResponse, order, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.order.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = await response.parse()
            assert_matches_type(OrderCreateResponse, order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncCadenza) -> None:
        order = await async_client.trading.order.list()
        assert_matches_type(AsyncOffset[Order], order, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCadenza) -> None:
        order = await async_client.trading.order.list(
            end_time=1632933600000,
            exchange_account_id="exchangeAccountId",
            limit=100,
            offset=0,
            order_id="orderId",
            order_status="SUBMITTED",
            start_time=1622505600000,
            symbol="symbol",
            tenant_id="tenantId",
        )
        assert_matches_type(AsyncOffset[Order], order, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.order.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = await response.parse()
        assert_matches_type(AsyncOffset[Order], order, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.order.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = await response.parse()
            assert_matches_type(AsyncOffset[Order], order, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncCadenza) -> None:
        order = await async_client.trading.order.cancel(
            order_id="orderId",
        )
        assert_matches_type(Order, order, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.order.with_raw_response.cancel(
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order = await response.parse()
        assert_matches_type(Order, order, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.order.with_streaming_response.cancel(
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order = await response.parse()
            assert_matches_type(Order, order, path=["response"])

        assert cast(Any, response.is_closed) is True
