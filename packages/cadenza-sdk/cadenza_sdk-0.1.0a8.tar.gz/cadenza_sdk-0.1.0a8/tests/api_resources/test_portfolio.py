# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types import (
    PortfolioListCreditResponse,
    PortfolioListBalancesResponse,
    PortfolioListPositionsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPortfolio:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list_balances(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_balances()
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    def test_method_list_balances_with_all_params(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_balances(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    def test_raw_response_list_balances(self, client: Cadenza) -> None:
        response = client.portfolio.with_raw_response.list_balances()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = response.parse()
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    def test_streaming_response_list_balances(self, client: Cadenza) -> None:
        with client.portfolio.with_streaming_response.list_balances() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = response.parse()
            assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_credit(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_credit()
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    def test_method_list_credit_with_all_params(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_credit(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    def test_raw_response_list_credit(self, client: Cadenza) -> None:
        response = client.portfolio.with_raw_response.list_credit()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = response.parse()
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    def test_streaming_response_list_credit(self, client: Cadenza) -> None:
        with client.portfolio.with_streaming_response.list_credit() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = response.parse()
            assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_positions(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_positions()
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    def test_method_list_positions_with_all_params(self, client: Cadenza) -> None:
        portfolio = client.portfolio.list_positions(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    def test_raw_response_list_positions(self, client: Cadenza) -> None:
        response = client.portfolio.with_raw_response.list_positions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = response.parse()
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    def test_streaming_response_list_positions(self, client: Cadenza) -> None:
        with client.portfolio.with_streaming_response.list_positions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = response.parse()
            assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPortfolio:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list_balances(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_balances()
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    async def test_method_list_balances_with_all_params(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_balances(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    async def test_raw_response_list_balances(self, async_client: AsyncCadenza) -> None:
        response = await async_client.portfolio.with_raw_response.list_balances()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = await response.parse()
        assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

    @parametrize
    async def test_streaming_response_list_balances(self, async_client: AsyncCadenza) -> None:
        async with async_client.portfolio.with_streaming_response.list_balances() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = await response.parse()
            assert_matches_type(PortfolioListBalancesResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_credit(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_credit()
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    async def test_method_list_credit_with_all_params(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_credit(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    async def test_raw_response_list_credit(self, async_client: AsyncCadenza) -> None:
        response = await async_client.portfolio.with_raw_response.list_credit()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = await response.parse()
        assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

    @parametrize
    async def test_streaming_response_list_credit(self, async_client: AsyncCadenza) -> None:
        async with async_client.portfolio.with_streaming_response.list_credit() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = await response.parse()
            assert_matches_type(PortfolioListCreditResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_positions(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_positions()
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    async def test_method_list_positions_with_all_params(self, async_client: AsyncCadenza) -> None:
        portfolio = await async_client.portfolio.list_positions(
            exchange_account_id="exchangeAccountId",
            hide_empty_value=True,
        )
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    async def test_raw_response_list_positions(self, async_client: AsyncCadenza) -> None:
        response = await async_client.portfolio.with_raw_response.list_positions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        portfolio = await response.parse()
        assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

    @parametrize
    async def test_streaming_response_list_positions(self, async_client: AsyncCadenza) -> None:
        async with async_client.portfolio.with_streaming_response.list_positions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            portfolio = await response.parse()
            assert_matches_type(PortfolioListPositionsResponse, portfolio, path=["response"])

        assert cast(Any, response.is_closed) is True
