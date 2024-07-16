# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cadenza_sdk import Cadenza, AsyncCadenza
from tests.utils import assert_matches_type
from cadenza_sdk.types.trading import (
    ExecutionReport,
    QuoteExecutionReport,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExecutionReport:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Cadenza) -> None:
        execution_report = client.trading.execution_report.list()
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Cadenza) -> None:
        execution_report = client.trading.execution_report.list(
            end_time=1632933600000,
            limit=100,
            offset=0,
            quote_request_id="quoteRequestId",
            start_time=1622505600000,
        )
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Cadenza) -> None:
        response = client.trading.execution_report.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execution_report = response.parse()
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Cadenza) -> None:
        with client.trading.execution_report.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execution_report = response.parse()
            assert_matches_type(ExecutionReport, execution_report, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_quote_execution_report(self, client: Cadenza) -> None:
        execution_report = client.trading.execution_report.get_quote_execution_report()
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_method_get_quote_execution_report_with_all_params(self, client: Cadenza) -> None:
        execution_report = client.trading.execution_report.get_quote_execution_report(
            quote_request_id="quoteRequestId",
        )
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_raw_response_get_quote_execution_report(self, client: Cadenza) -> None:
        response = client.trading.execution_report.with_raw_response.get_quote_execution_report()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execution_report = response.parse()
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    def test_streaming_response_get_quote_execution_report(self, client: Cadenza) -> None:
        with client.trading.execution_report.with_streaming_response.get_quote_execution_report() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execution_report = response.parse()
            assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExecutionReport:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncCadenza) -> None:
        execution_report = await async_client.trading.execution_report.list()
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCadenza) -> None:
        execution_report = await async_client.trading.execution_report.list(
            end_time=1632933600000,
            limit=100,
            offset=0,
            quote_request_id="quoteRequestId",
            start_time=1622505600000,
        )
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.execution_report.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execution_report = await response.parse()
        assert_matches_type(ExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.execution_report.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execution_report = await response.parse()
            assert_matches_type(ExecutionReport, execution_report, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_quote_execution_report(self, async_client: AsyncCadenza) -> None:
        execution_report = await async_client.trading.execution_report.get_quote_execution_report()
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_method_get_quote_execution_report_with_all_params(self, async_client: AsyncCadenza) -> None:
        execution_report = await async_client.trading.execution_report.get_quote_execution_report(
            quote_request_id="quoteRequestId",
        )
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_raw_response_get_quote_execution_report(self, async_client: AsyncCadenza) -> None:
        response = await async_client.trading.execution_report.with_raw_response.get_quote_execution_report()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        execution_report = await response.parse()
        assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

    @parametrize
    async def test_streaming_response_get_quote_execution_report(self, async_client: AsyncCadenza) -> None:
        async with async_client.trading.execution_report.with_streaming_response.get_quote_execution_report() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            execution_report = await response.parse()
            assert_matches_type(QuoteExecutionReport, execution_report, path=["response"])

        assert cast(Any, response.is_closed) is True
