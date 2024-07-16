# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.market import KlineGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestKline:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get(self, client: Cadenza) -> None:
        kline = client.market.kline.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        )
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    def test_method_get_with_all_params(self, client: Cadenza) -> None:
        kline = client.market.kline.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
            end_time=1632933600000,
            limit=100,
            start_time=1622505600000,
        )
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Cadenza) -> None:
        response = client.market.kline.with_raw_response.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kline = response.parse()
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Cadenza) -> None:
        with client.market.kline.with_streaming_response.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kline = response.parse()
            assert_matches_type(KlineGetResponse, kline, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncKline:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_get(self, async_client: AsyncCadenza) -> None:
        kline = await async_client.market.kline.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        )
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncCadenza) -> None:
        kline = await async_client.market.kline.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
            end_time=1632933600000,
            limit=100,
            start_time=1622505600000,
        )
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCadenza) -> None:
        response = await async_client.market.kline.with_raw_response.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kline = await response.parse()
        assert_matches_type(KlineGetResponse, kline, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCadenza) -> None:
        async with async_client.market.kline.with_streaming_response.get(
            exchange_type="BINANCE",
            interval="1s",
            symbol="BTC/USDT",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kline = await response.parse()
            assert_matches_type(KlineGetResponse, kline, path=["response"])

        assert cast(Any, response.is_closed) is True
