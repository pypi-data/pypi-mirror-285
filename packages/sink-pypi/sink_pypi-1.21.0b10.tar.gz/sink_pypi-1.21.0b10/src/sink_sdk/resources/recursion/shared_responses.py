# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.shared.shared_self_recursion import SharedSelfRecursion

__all__ = ["SharedResponsesResource", "AsyncSharedResponsesResource"]


class SharedResponsesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SharedResponsesResourceWithRawResponse:
        return SharedResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SharedResponsesResourceWithStreamingResponse:
        return SharedResponsesResourceWithStreamingResponse(self)

    def create_self(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> SharedSelfRecursion:
        return self._post(
            "/recursion/shared/responses/self",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=SharedSelfRecursion,
        )


class AsyncSharedResponsesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSharedResponsesResourceWithRawResponse:
        return AsyncSharedResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSharedResponsesResourceWithStreamingResponse:
        return AsyncSharedResponsesResourceWithStreamingResponse(self)

    async def create_self(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> SharedSelfRecursion:
        return await self._post(
            "/recursion/shared/responses/self",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=SharedSelfRecursion,
        )


class SharedResponsesResourceWithRawResponse:
    def __init__(self, shared_responses: SharedResponsesResource) -> None:
        self._shared_responses = shared_responses

        self.create_self = to_raw_response_wrapper(
            shared_responses.create_self,
        )


class AsyncSharedResponsesResourceWithRawResponse:
    def __init__(self, shared_responses: AsyncSharedResponsesResource) -> None:
        self._shared_responses = shared_responses

        self.create_self = async_to_raw_response_wrapper(
            shared_responses.create_self,
        )


class SharedResponsesResourceWithStreamingResponse:
    def __init__(self, shared_responses: SharedResponsesResource) -> None:
        self._shared_responses = shared_responses

        self.create_self = to_streamed_response_wrapper(
            shared_responses.create_self,
        )


class AsyncSharedResponsesResourceWithStreamingResponse:
    def __init__(self, shared_responses: AsyncSharedResponsesResource) -> None:
        self._shared_responses = shared_responses

        self.create_self = async_to_streamed_response_wrapper(
            shared_responses.create_self,
        )
