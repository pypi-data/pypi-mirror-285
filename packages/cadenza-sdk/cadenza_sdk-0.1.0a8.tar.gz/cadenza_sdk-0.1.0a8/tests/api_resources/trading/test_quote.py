# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.trading import QuoteRequestForQuoteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQuote:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_request_for_quote(self, client: Cadenza) -> None:
        quote = client.trading.quote.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        )
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    def test_method_request_for_quote_with_all_params(self, client: Cadenza) -> None:
        quote = client.trading.quote.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            quantity=0,
            quote_quantity=0,
        )
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    def test_raw_response_request_for_quote(self, client: Cadenza) -> None:
        response = client.trading.quote.with_raw_response.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quote = response.parse()
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    def test_streaming_response_request_for_quote(self, client: Cadenza) -> None:
        with client.trading.quote.with_streaming_response.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quote = response.parse()
            assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncQuote:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_request_for_quote(self, async_client: AsyncCadenza) -> None:
        quote = await async_client.trading.quote.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        )
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    async def test_method_request_for_quote_with_all_params(self, async_client: AsyncCadenza) -> None:
        quote = await async_client.trading.quote.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
            exchange_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            quantity=0,
            quote_quantity=0,
        )
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    async def test_raw_response_request_for_quote(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.quote.with_raw_response.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quote = await response.parse()
        assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

    @parametrize
    async def test_streaming_response_request_for_quote(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.quote.with_streaming_response.request_for_quote(
            base_currency="baseCurrency",
            order_side="orderSide",
            quote_currency="quoteCurrency",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quote = await response.parse()
            assert_matches_type(QuoteRequestForQuoteResponse, quote, path=["response"])

        assert cast(Any, response.is_closed) is True
