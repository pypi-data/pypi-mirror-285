# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.market import OrderbookGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrderbook:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get(self, client: Cadenza) -> None:
        orderbook = client.market.orderbook.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        )
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Cadenza) -> None:
        orderbook = client.market.orderbook.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
            limit=100,
        )
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Cadenza) -> None:
        response = client.market.orderbook.with_raw_response.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        orderbook = response.parse()
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Cadenza) -> None:
        with client.market.orderbook.with_streaming_response.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            orderbook = response.parse()
            assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOrderbook:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_get(self, async_client: AsyncCadenza) -> None:
        orderbook = await async_client.market.orderbook.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        )
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncCadenza) -> None:
        orderbook = await async_client.market.orderbook.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
            limit=100,
        )
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCadenza) -> None:
        response = await async_client.market.orderbook.with_raw_response.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        orderbook = await response.parse()
        assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCadenza) -> None:
        async with async_client.market.orderbook.with_streaming_response.get(
            exchange_type="BINANCE",
            symbol="BTC/USDT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            orderbook = await response.parse()
            assert_matches_type(OrderbookGetResponse, orderbook, path=["response"])

        assert cast(Any, response.is_closed) is True
