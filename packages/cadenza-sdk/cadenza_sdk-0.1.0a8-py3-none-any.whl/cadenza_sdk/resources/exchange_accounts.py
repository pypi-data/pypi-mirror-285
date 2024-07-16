# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import (
    exchange_account_create_params,
    exchange_account_remove_params,
    exchange_account_update_params,
    exchange_account_set_exchange_priority_params,
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
from ..types.exchange_account_list_response import ExchangeAccountListResponse
from ..types.exchange_account_create_response import ExchangeAccountCreateResponse
from ..types.exchange_account_remove_response import ExchangeAccountRemoveResponse
from ..types.exchange_account_update_response import ExchangeAccountUpdateResponse
from ..types.exchange_account_set_exchange_priority_response import ExchangeAccountSetExchangePriorityResponse

__all__ = ["ExchangeAccountsResource", "AsyncExchangeAccountsResource"]


class ExchangeAccountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExchangeAccountsResourceWithRawResponse:
        return ExchangeAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExchangeAccountsResourceWithStreamingResponse:
        return ExchangeAccountsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_key: str,
        api_secret: str,
        environment: Literal[0, 1],
        exchange_account_name: str,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountCreateResponse:
        """
        Add exchange account

        Args:
          api_key: API key

          api_secret: API secret

          environment: Environment(0 - real, 1 - sandbox)

          exchange_account_name: Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)

          exchange_type: Exchange type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/exchange/addExchangeAccount",
            body=maybe_transform(
                {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "environment": environment,
                    "exchange_account_name": exchange_account_name,
                    "exchange_type": exchange_type,
                },
                exchange_account_create_params.ExchangeAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountCreateResponse,
        )

    def update(
        self,
        *,
        exchange_account_id: str,
        api_key: str | NotGiven = NOT_GIVEN,
        api_secret: str | NotGiven = NOT_GIVEN,
        exchange_account_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountUpdateResponse:
        """
        Update exchange account, now only support Binance account API key and secret

        Args:
          exchange_account_id: Exchange account ID

          api_key: API key

          api_secret: API secret

          exchange_account_name: Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/exchange/updateExchangeAccount",
            body=maybe_transform(
                {
                    "exchange_account_id": exchange_account_id,
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "exchange_account_name": exchange_account_name,
                },
                exchange_account_update_params.ExchangeAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountUpdateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountListResponse:
        """List exchange accounts"""
        return self._get(
            "/api/v2/exchange/listExchangeAccounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountListResponse,
        )

    def remove(
        self,
        *,
        exchange_account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountRemoveResponse:
        """
        Remove exchange account, now only support Binance account API key and secret

        Args:
          exchange_account_id: Exchange account ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/exchange/removeExchangeAccount",
            body=maybe_transform(
                {"exchange_account_id": exchange_account_id}, exchange_account_remove_params.ExchangeAccountRemoveParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountRemoveResponse,
        )

    def set_exchange_priority(
        self,
        *,
        priority: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountSetExchangePriorityResponse:
        """
        Set the priority of exchanges

        Args:
          priority: Priority list of exchanges in descending order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/exchange/setExchangePriority",
            body=maybe_transform(
                {"priority": priority},
                exchange_account_set_exchange_priority_params.ExchangeAccountSetExchangePriorityParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountSetExchangePriorityResponse,
        )


class AsyncExchangeAccountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExchangeAccountsResourceWithRawResponse:
        return AsyncExchangeAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExchangeAccountsResourceWithStreamingResponse:
        return AsyncExchangeAccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_key: str,
        api_secret: str,
        environment: Literal[0, 1],
        exchange_account_name: str,
        exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountCreateResponse:
        """
        Add exchange account

        Args:
          api_key: API key

          api_secret: API secret

          environment: Environment(0 - real, 1 - sandbox)

          exchange_account_name: Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)

          exchange_type: Exchange type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/exchange/addExchangeAccount",
            body=await async_maybe_transform(
                {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "environment": environment,
                    "exchange_account_name": exchange_account_name,
                    "exchange_type": exchange_type,
                },
                exchange_account_create_params.ExchangeAccountCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountCreateResponse,
        )

    async def update(
        self,
        *,
        exchange_account_id: str,
        api_key: str | NotGiven = NOT_GIVEN,
        api_secret: str | NotGiven = NOT_GIVEN,
        exchange_account_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountUpdateResponse:
        """
        Update exchange account, now only support Binance account API key and secret

        Args:
          exchange_account_id: Exchange account ID

          api_key: API key

          api_secret: API secret

          exchange_account_name: Exchange account name, Available characters: a-z, A-Z, 0-9, \\__, ' '(space)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/exchange/updateExchangeAccount",
            body=await async_maybe_transform(
                {
                    "exchange_account_id": exchange_account_id,
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "exchange_account_name": exchange_account_name,
                },
                exchange_account_update_params.ExchangeAccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountUpdateResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountListResponse:
        """List exchange accounts"""
        return await self._get(
            "/api/v2/exchange/listExchangeAccounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountListResponse,
        )

    async def remove(
        self,
        *,
        exchange_account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountRemoveResponse:
        """
        Remove exchange account, now only support Binance account API key and secret

        Args:
          exchange_account_id: Exchange account ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/exchange/removeExchangeAccount",
            body=await async_maybe_transform(
                {"exchange_account_id": exchange_account_id}, exchange_account_remove_params.ExchangeAccountRemoveParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountRemoveResponse,
        )

    async def set_exchange_priority(
        self,
        *,
        priority: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExchangeAccountSetExchangePriorityResponse:
        """
        Set the priority of exchanges

        Args:
          priority: Priority list of exchanges in descending order

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/exchange/setExchangePriority",
            body=await async_maybe_transform(
                {"priority": priority},
                exchange_account_set_exchange_priority_params.ExchangeAccountSetExchangePriorityParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExchangeAccountSetExchangePriorityResponse,
        )


class ExchangeAccountsResourceWithRawResponse:
    def __init__(self, exchange_accounts: ExchangeAccountsResource) -> None:
        self._exchange_accounts = exchange_accounts

        self.create = to_raw_response_wrapper(
            exchange_accounts.create,
        )
        self.update = to_raw_response_wrapper(
            exchange_accounts.update,
        )
        self.list = to_raw_response_wrapper(
            exchange_accounts.list,
        )
        self.remove = to_raw_response_wrapper(
            exchange_accounts.remove,
        )
        self.set_exchange_priority = to_raw_response_wrapper(
            exchange_accounts.set_exchange_priority,
        )


class AsyncExchangeAccountsResourceWithRawResponse:
    def __init__(self, exchange_accounts: AsyncExchangeAccountsResource) -> None:
        self._exchange_accounts = exchange_accounts

        self.create = async_to_raw_response_wrapper(
            exchange_accounts.create,
        )
        self.update = async_to_raw_response_wrapper(
            exchange_accounts.update,
        )
        self.list = async_to_raw_response_wrapper(
            exchange_accounts.list,
        )
        self.remove = async_to_raw_response_wrapper(
            exchange_accounts.remove,
        )
        self.set_exchange_priority = async_to_raw_response_wrapper(
            exchange_accounts.set_exchange_priority,
        )


class ExchangeAccountsResourceWithStreamingResponse:
    def __init__(self, exchange_accounts: ExchangeAccountsResource) -> None:
        self._exchange_accounts = exchange_accounts

        self.create = to_streamed_response_wrapper(
            exchange_accounts.create,
        )
        self.update = to_streamed_response_wrapper(
            exchange_accounts.update,
        )
        self.list = to_streamed_response_wrapper(
            exchange_accounts.list,
        )
        self.remove = to_streamed_response_wrapper(
            exchange_accounts.remove,
        )
        self.set_exchange_priority = to_streamed_response_wrapper(
            exchange_accounts.set_exchange_priority,
        )


class AsyncExchangeAccountsResourceWithStreamingResponse:
    def __init__(self, exchange_accounts: AsyncExchangeAccountsResource) -> None:
        self._exchange_accounts = exchange_accounts

        self.create = async_to_streamed_response_wrapper(
            exchange_accounts.create,
        )
        self.update = async_to_streamed_response_wrapper(
            exchange_accounts.update,
        )
        self.list = async_to_streamed_response_wrapper(
            exchange_accounts.list,
        )
        self.remove = async_to_streamed_response_wrapper(
            exchange_accounts.remove,
        )
        self.set_exchange_priority = async_to_streamed_response_wrapper(
            exchange_accounts.set_exchange_priority,
        )
