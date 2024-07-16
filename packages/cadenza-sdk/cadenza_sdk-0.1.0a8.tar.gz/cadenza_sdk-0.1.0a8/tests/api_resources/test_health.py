# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHealth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get(self, client: Cadenza) -> None:
        health = client.health.get()
        assert_matches_type(str, health, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Cadenza) -> None:
        response = client.health.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        health = response.parse()
        assert_matches_type(str, health, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Cadenza) -> None:
        with client.health.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            health = response.parse()
            assert_matches_type(str, health, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncHealth:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_get(self, async_client: AsyncCadenza) -> None:
        health = await async_client.health.get()
        assert_matches_type(str, health, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCadenza) -> None:
        response = await async_client.health.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        health = await response.parse()
        assert_matches_type(str, health, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCadenza) -> None:
        async with async_client.health.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            health = await response.parse()
            assert_matches_type(str, health, path=["response"])

        assert cast(Any, response.is_closed) is True
