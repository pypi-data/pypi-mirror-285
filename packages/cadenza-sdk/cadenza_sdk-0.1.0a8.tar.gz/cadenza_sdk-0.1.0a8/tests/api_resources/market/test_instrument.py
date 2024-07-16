# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.market import InstrumentListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInstrument:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Cadenza) -> None:
        instrument = client.market.instrument.list()
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Cadenza) -> None:
        instrument = client.market.instrument.list(
            detail=False,
            exchange_type="BINANCE",
            symbol="symbol",
        )
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Cadenza) -> None:
        response = client.market.instrument.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        instrument = response.parse()
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Cadenza) -> None:
        with client.market.instrument.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            instrument = response.parse()
            assert_matches_type(InstrumentListResponse, instrument, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncInstrument:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncCadenza) -> None:
        instrument = await async_client.market.instrument.list()
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCadenza) -> None:
        instrument = await async_client.market.instrument.list(
            detail=False,
            exchange_type="BINANCE",
            symbol="symbol",
        )
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCadenza) -> None:
        response = await async_client.market.instrument.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        instrument = await response.parse()
        assert_matches_type(InstrumentListResponse, instrument, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCadenza) -> None:
        async with async_client.market.instrument.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            instrument = await response.parse()
            assert_matches_type(InstrumentListResponse, instrument, path=["response"])

        assert cast(Any, response.is_closed) is True
