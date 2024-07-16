# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["HealthResource", "AsyncHealthResource"]


class HealthResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HealthResourceWithRawResponse:
        return HealthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HealthResourceWithStreamingResponse:
        return HealthResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """Health check"""
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._get(
            "/api/v2/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class AsyncHealthResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHealthResourceWithRawResponse:
        return AsyncHealthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHealthResourceWithStreamingResponse:
        return AsyncHealthResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """Health check"""
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._get(
            "/api/v2/health",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class HealthResourceWithRawResponse:
    def __init__(self, health: HealthResource) -> None:
        self._health = health

        self.get = to_raw_response_wrapper(
            health.get,
        )


class AsyncHealthResourceWithRawResponse:
    def __init__(self, health: AsyncHealthResource) -> None:
        self._health = health

        self.get = async_to_raw_response_wrapper(
            health.get,
        )


class HealthResourceWithStreamingResponse:
    def __init__(self, health: HealthResource) -> None:
        self._health = health

        self.get = to_streamed_response_wrapper(
            health.get,
        )


class AsyncHealthResourceWithStreamingResponse:
    def __init__(self, health: AsyncHealthResource) -> None:
        self._health = health

        self.get = async_to_streamed_response_wrapper(
            health.get,
        )
