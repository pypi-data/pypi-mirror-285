# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types import (
    ExchangeAccountListResponse,
    ExchangeAccountCreateResponse,
    ExchangeAccountRemoveResponse,
    ExchangeAccountUpdateResponse,
    ExchangeAccountSetExchangePriorityResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExchangeAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        )
        assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Cadenza) -> None:
        response = client.exchange_accounts.with_raw_response.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = response.parse()
        assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Cadenza) -> None:
        with client.exchange_accounts.with_streaming_response.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = response.parse()
            assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            api_key="my_api_key",
            api_secret="my_api_secret",
            exchange_account_name="my_exchange",
        )
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Cadenza) -> None:
        response = client.exchange_accounts.with_raw_response.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = response.parse()
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Cadenza) -> None:
        with client.exchange_accounts.with_streaming_response.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = response.parse()
            assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.list()
        assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Cadenza) -> None:
        response = client.exchange_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = response.parse()
        assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Cadenza) -> None:
        with client.exchange_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = response.parse()
            assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_remove(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

    @parametrize
    def test_raw_response_remove(self, client: Cadenza) -> None:
        response = client.exchange_accounts.with_raw_response.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = response.parse()
        assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

    @parametrize
    def test_streaming_response_remove(self, client: Cadenza) -> None:
        with client.exchange_accounts.with_streaming_response.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = response.parse()
            assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_set_exchange_priority(self, client: Cadenza) -> None:
        exchange_account = client.exchange_accounts.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        )
        assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

    @parametrize
    def test_raw_response_set_exchange_priority(self, client: Cadenza) -> None:
        response = client.exchange_accounts.with_raw_response.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = response.parse()
        assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

    @parametrize
    def test_streaming_response_set_exchange_priority(self, client: Cadenza) -> None:
        with client.exchange_accounts.with_streaming_response.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = response.parse()
            assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExchangeAccounts:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        )
        assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncCadenza) -> None:
        response = await async_client.exchange_accounts.with_raw_response.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = await response.parse()
        assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncCadenza) -> None:
        async with async_client.exchange_accounts.with_streaming_response.create(
            api_key="my_api_key",
            api_secret="my_api_secret",
            environment=0,
            exchange_account_name="my_exchange",
            exchange_type="BINANCE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = await response.parse()
            assert_matches_type(ExchangeAccountCreateResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            api_key="my_api_key",
            api_secret="my_api_secret",
            exchange_account_name="my_exchange",
        )
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncCadenza) -> None:
        response = await async_client.exchange_accounts.with_raw_response.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = await response.parse()
        assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncCadenza) -> None:
        async with async_client.exchange_accounts.with_streaming_response.update(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = await response.parse()
            assert_matches_type(ExchangeAccountUpdateResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.list()
        assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCadenza) -> None:
        response = await async_client.exchange_accounts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = await response.parse()
        assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCadenza) -> None:
        async with async_client.exchange_accounts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = await response.parse()
            assert_matches_type(ExchangeAccountListResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_remove(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

    @parametrize
    async def test_raw_response_remove(self, async_client: AsyncCadenza) -> None:
        response = await async_client.exchange_accounts.with_raw_response.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = await response.parse()
        assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

    @parametrize
    async def test_streaming_response_remove(self, async_client: AsyncCadenza) -> None:
        async with async_client.exchange_accounts.with_streaming_response.remove(
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = await response.parse()
            assert_matches_type(ExchangeAccountRemoveResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_set_exchange_priority(self, async_client: AsyncCadenza) -> None:
        exchange_account = await async_client.exchange_accounts.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        )
        assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

    @parametrize
    async def test_raw_response_set_exchange_priority(self, async_client: AsyncCadenza) -> None:
        response = await async_client.exchange_accounts.with_raw_response.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        exchange_account = await response.parse()
        assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

    @parametrize
    async def test_streaming_response_set_exchange_priority(self, async_client: AsyncCadenza) -> None:
        async with async_client.exchange_accounts.with_streaming_response.set_exchange_priority(
            priority=["my_exchange_1", "my_exchange_2", "my_exchange_3"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            exchange_account = await response.parse()
            assert_matches_type(ExchangeAccountSetExchangePriorityResponse, exchange_account, path=["response"])

        assert cast(Any, response.is_closed) is True
