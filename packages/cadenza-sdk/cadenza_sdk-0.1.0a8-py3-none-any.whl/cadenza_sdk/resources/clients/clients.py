# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .info import (
    InfoResource,
    AsyncInfoResource,
    InfoResourceWithRawResponse,
    AsyncInfoResourceWithRawResponse,
    InfoResourceWithStreamingResponse,
    AsyncInfoResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ClientsResource", "AsyncClientsResource"]


class ClientsResource(SyncAPIResource):
    @cached_property
    def info(self) -> InfoResource:
        return InfoResource(self._client)

    @cached_property
    def with_raw_response(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self)


class AsyncClientsResource(AsyncAPIResource):
    @cached_property
    def info(self) -> AsyncInfoResource:
        return AsyncInfoResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self)


class ClientsResourceWithRawResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

    @cached_property
    def info(self) -> InfoResourceWithRawResponse:
        return InfoResourceWithRawResponse(self._clients.info)


class AsyncClientsResourceWithRawResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

    @cached_property
    def info(self) -> AsyncInfoResourceWithRawResponse:
        return AsyncInfoResourceWithRawResponse(self._clients.info)


class ClientsResourceWithStreamingResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

    @cached_property
    def info(self) -> InfoResourceWithStreamingResponse:
        return InfoResourceWithStreamingResponse(self._clients.info)


class AsyncClientsResourceWithStreamingResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

    @cached_property
    def info(self) -> AsyncInfoResourceWithStreamingResponse:
        return AsyncInfoResourceWithStreamingResponse(self._clients.info)
