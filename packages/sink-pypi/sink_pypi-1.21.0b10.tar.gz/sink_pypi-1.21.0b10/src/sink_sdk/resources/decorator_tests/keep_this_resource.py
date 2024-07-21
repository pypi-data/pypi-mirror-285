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
from ...types.decorator_tests.keep_this_resource_keep_this_method_response import KeepThisResourceKeepThisMethodResponse

__all__ = ["KeepThisResourceResource", "AsyncKeepThisResourceResource"]


class KeepThisResourceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KeepThisResourceResourceWithRawResponse:
        return KeepThisResourceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KeepThisResourceResourceWithStreamingResponse:
        return KeepThisResourceResourceWithStreamingResponse(self)

    def keep_this_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeepThisResourceKeepThisMethodResponse:
        """
        Nested method that should render because it is not skipped nor are its
        ancestors.
        """
        return self._get(
            "/decorator_tests/nested/keep/this/method",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeepThisResourceKeepThisMethodResponse,
        )


class AsyncKeepThisResourceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKeepThisResourceResourceWithRawResponse:
        return AsyncKeepThisResourceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKeepThisResourceResourceWithStreamingResponse:
        return AsyncKeepThisResourceResourceWithStreamingResponse(self)

    async def keep_this_method(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeepThisResourceKeepThisMethodResponse:
        """
        Nested method that should render because it is not skipped nor are its
        ancestors.
        """
        return await self._get(
            "/decorator_tests/nested/keep/this/method",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeepThisResourceKeepThisMethodResponse,
        )


class KeepThisResourceResourceWithRawResponse:
    def __init__(self, keep_this_resource: KeepThisResourceResource) -> None:
        self._keep_this_resource = keep_this_resource

        self.keep_this_method = to_raw_response_wrapper(
            keep_this_resource.keep_this_method,
        )


class AsyncKeepThisResourceResourceWithRawResponse:
    def __init__(self, keep_this_resource: AsyncKeepThisResourceResource) -> None:
        self._keep_this_resource = keep_this_resource

        self.keep_this_method = async_to_raw_response_wrapper(
            keep_this_resource.keep_this_method,
        )


class KeepThisResourceResourceWithStreamingResponse:
    def __init__(self, keep_this_resource: KeepThisResourceResource) -> None:
        self._keep_this_resource = keep_this_resource

        self.keep_this_method = to_streamed_response_wrapper(
            keep_this_resource.keep_this_method,
        )


class AsyncKeepThisResourceResourceWithStreamingResponse:
    def __init__(self, keep_this_resource: AsyncKeepThisResourceResource) -> None:
        self._keep_this_resource = keep_this_resource

        self.keep_this_method = async_to_streamed_response_wrapper(
            keep_this_resource.keep_this_method,
        )
