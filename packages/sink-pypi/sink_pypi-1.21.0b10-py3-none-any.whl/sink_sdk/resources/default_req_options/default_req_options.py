# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .child import (
    ChildResource,
    AsyncChildResource,
    ChildResourceWithRawResponse,
    AsyncChildResourceWithRawResponse,
    ChildResourceWithStreamingResponse,
    AsyncChildResourceWithStreamingResponse,
)
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
from ...types.shared.basic_shared_model_object import BasicSharedModelObject

__all__ = ["DefaultReqOptionsResource", "AsyncDefaultReqOptionsResource"]


class DefaultReqOptionsResource(SyncAPIResource):
    @cached_property
    def child(self) -> ChildResource:
        return ChildResource(self._client)

    @cached_property
    def with_raw_response(self) -> DefaultReqOptionsResourceWithRawResponse:
        return DefaultReqOptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DefaultReqOptionsResourceWithStreamingResponse:
        return DefaultReqOptionsResourceWithStreamingResponse(self)

    def example_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BasicSharedModelObject:
        """Testing resource level default request options."""
        extra_headers = {"X-My-Header": "true", "X-My-Other-Header": "false", **(extra_headers or {})}
        return self._get(
            "/default_req_options",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BasicSharedModelObject,
        )


class AsyncDefaultReqOptionsResource(AsyncAPIResource):
    @cached_property
    def child(self) -> AsyncChildResource:
        return AsyncChildResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDefaultReqOptionsResourceWithRawResponse:
        return AsyncDefaultReqOptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDefaultReqOptionsResourceWithStreamingResponse:
        return AsyncDefaultReqOptionsResourceWithStreamingResponse(self)

    async def example_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BasicSharedModelObject:
        """Testing resource level default request options."""
        extra_headers = {"X-My-Header": "true", "X-My-Other-Header": "false", **(extra_headers or {})}
        return await self._get(
            "/default_req_options",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BasicSharedModelObject,
        )


class DefaultReqOptionsResourceWithRawResponse:
    def __init__(self, default_req_options: DefaultReqOptionsResource) -> None:
        self._default_req_options = default_req_options

        self.example_method = to_raw_response_wrapper(
            default_req_options.example_method,
        )

    @cached_property
    def child(self) -> ChildResourceWithRawResponse:
        return ChildResourceWithRawResponse(self._default_req_options.child)


class AsyncDefaultReqOptionsResourceWithRawResponse:
    def __init__(self, default_req_options: AsyncDefaultReqOptionsResource) -> None:
        self._default_req_options = default_req_options

        self.example_method = async_to_raw_response_wrapper(
            default_req_options.example_method,
        )

    @cached_property
    def child(self) -> AsyncChildResourceWithRawResponse:
        return AsyncChildResourceWithRawResponse(self._default_req_options.child)


class DefaultReqOptionsResourceWithStreamingResponse:
    def __init__(self, default_req_options: DefaultReqOptionsResource) -> None:
        self._default_req_options = default_req_options

        self.example_method = to_streamed_response_wrapper(
            default_req_options.example_method,
        )

    @cached_property
    def child(self) -> ChildResourceWithStreamingResponse:
        return ChildResourceWithStreamingResponse(self._default_req_options.child)


class AsyncDefaultReqOptionsResourceWithStreamingResponse:
    def __init__(self, default_req_options: AsyncDefaultReqOptionsResource) -> None:
        self._default_req_options = default_req_options

        self.example_method = async_to_streamed_response_wrapper(
            default_req_options.example_method,
        )

    @cached_property
    def child(self) -> AsyncChildResourceWithStreamingResponse:
        return AsyncChildResourceWithStreamingResponse(self._default_req_options.child)
