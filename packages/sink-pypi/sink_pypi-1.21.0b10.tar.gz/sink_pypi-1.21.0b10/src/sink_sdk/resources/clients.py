# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import client_create_params
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
from ..types.client import Client

__all__ = ["ClientsResource", "AsyncClientsResource"]


class ClientsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClientsResourceWithRawResponse:
        return ClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClientsResourceWithStreamingResponse:
        return ClientsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_token: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Client:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/clients",
            body=maybe_transform(
                {
                    "account_token": account_token,
                    "name": name,
                },
                client_create_params.ClientCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Client,
        )


class AsyncClientsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClientsResourceWithRawResponse:
        return AsyncClientsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClientsResourceWithStreamingResponse:
        return AsyncClientsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_token: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Client:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/clients",
            body=await async_maybe_transform(
                {
                    "account_token": account_token,
                    "name": name,
                },
                client_create_params.ClientCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=Client,
        )


class ClientsResourceWithRawResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

        self.create = to_raw_response_wrapper(
            clients.create,
        )


class AsyncClientsResourceWithRawResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

        self.create = async_to_raw_response_wrapper(
            clients.create,
        )


class ClientsResourceWithStreamingResponse:
    def __init__(self, clients: ClientsResource) -> None:
        self._clients = clients

        self.create = to_streamed_response_wrapper(
            clients.create,
        )


class AsyncClientsResourceWithStreamingResponse:
    def __init__(self, clients: AsyncClientsResource) -> None:
        self._clients = clients

        self.create = async_to_streamed_response_wrapper(
            clients.create,
        )
