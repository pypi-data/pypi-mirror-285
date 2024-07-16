# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    portfolio_list_credit_params,
    portfolio_list_balances_params,
    portfolio_list_positions_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.portfolio_list_credit_response import PortfolioListCreditResponse
from ..types.portfolio_list_balances_response import PortfolioListBalancesResponse
from ..types.portfolio_list_positions_response import PortfolioListPositionsResponse

__all__ = ["PortfolioResource", "AsyncPortfolioResource"]


class PortfolioResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PortfolioResourceWithRawResponse:
        return PortfolioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PortfolioResourceWithStreamingResponse:
        return PortfolioResourceWithStreamingResponse(self)

    def list_balances(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListBalancesResponse:
        """
        List balances

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/portfolio/listBalances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_balances_params.PortfolioListBalancesParams,
                ),
            ),
            cast_to=PortfolioListBalancesResponse,
        )

    def list_credit(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListCreditResponse:
        """
        List credit

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/portfolio/listCredit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_credit_params.PortfolioListCreditParams,
                ),
            ),
            cast_to=PortfolioListCreditResponse,
        )

    def list_positions(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListPositionsResponse:
        """
        List positions

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/portfolio/listPositions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_positions_params.PortfolioListPositionsParams,
                ),
            ),
            cast_to=PortfolioListPositionsResponse,
        )


class AsyncPortfolioResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPortfolioResourceWithRawResponse:
        return AsyncPortfolioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPortfolioResourceWithStreamingResponse:
        return AsyncPortfolioResourceWithStreamingResponse(self)

    async def list_balances(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListBalancesResponse:
        """
        List balances

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/portfolio/listBalances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_balances_params.PortfolioListBalancesParams,
                ),
            ),
            cast_to=PortfolioListBalancesResponse,
        )

    async def list_credit(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListCreditResponse:
        """
        List credit

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/portfolio/listCredit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_credit_params.PortfolioListCreditParams,
                ),
            ),
            cast_to=PortfolioListCreditResponse,
        )

    async def list_positions(
        self,
        *,
        exchange_account_id: str | NotGiven = NOT_GIVEN,
        hide_empty_value: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PortfolioListPositionsResponse:
        """
        List positions

        Args:
          exchange_account_id: Exchange account ID

          hide_empty_value: Hide small account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/portfolio/listPositions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exchange_account_id": exchange_account_id,
                        "hide_empty_value": hide_empty_value,
                    },
                    portfolio_list_positions_params.PortfolioListPositionsParams,
                ),
            ),
            cast_to=PortfolioListPositionsResponse,
        )


class PortfolioResourceWithRawResponse:
    def __init__(self, portfolio: PortfolioResource) -> None:
        self._portfolio = portfolio

        self.list_balances = to_raw_response_wrapper(
            portfolio.list_balances,
        )
        self.list_credit = to_raw_response_wrapper(
            portfolio.list_credit,
        )
        self.list_positions = to_raw_response_wrapper(
            portfolio.list_positions,
        )


class AsyncPortfolioResourceWithRawResponse:
    def __init__(self, portfolio: AsyncPortfolioResource) -> None:
        self._portfolio = portfolio

        self.list_balances = async_to_raw_response_wrapper(
            portfolio.list_balances,
        )
        self.list_credit = async_to_raw_response_wrapper(
            portfolio.list_credit,
        )
        self.list_positions = async_to_raw_response_wrapper(
            portfolio.list_positions,
        )


class PortfolioResourceWithStreamingResponse:
    def __init__(self, portfolio: PortfolioResource) -> None:
        self._portfolio = portfolio

        self.list_balances = to_streamed_response_wrapper(
            portfolio.list_balances,
        )
        self.list_credit = to_streamed_response_wrapper(
            portfolio.list_credit,
        )
        self.list_positions = to_streamed_response_wrapper(
            portfolio.list_positions,
        )


class AsyncPortfolioResourceWithStreamingResponse:
    def __init__(self, portfolio: AsyncPortfolioResource) -> None:
        self._portfolio = portfolio

        self.list_balances = async_to_streamed_response_wrapper(
            portfolio.list_balances,
        )
        self.list_credit = async_to_streamed_response_wrapper(
            portfolio.list_credit,
        )
        self.list_positions = async_to_streamed_response_wrapper(
            portfolio.list_positions,
        )
