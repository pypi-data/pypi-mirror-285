# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.clients import InfoGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInfo:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get(self, client: Cadenza) -> None:
        info = client.clients.info.get()
        assert_matches_type(InfoGetResponse, info, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Cadenza) -> None:
        response = client.clients.info.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        info = response.parse()
        assert_matches_type(InfoGetResponse, info, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Cadenza) -> None:
        with client.clients.info.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            info = response.parse()
            assert_matches_type(InfoGetResponse, info, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncInfo:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_get(self, async_client: AsyncCadenza) -> None:
        info = await async_client.clients.info.get()
        assert_matches_type(InfoGetResponse, info, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncCadenza) -> None:
        response = await async_client.clients.info.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        info = await response.parse()
        assert_matches_type(InfoGetResponse, info, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncCadenza) -> None:
        async with async_client.clients.info.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            info = await response.parse()
            assert_matches_type(InfoGetResponse, info, path=["response"])

        assert cast(Any, response.is_closed) is True
