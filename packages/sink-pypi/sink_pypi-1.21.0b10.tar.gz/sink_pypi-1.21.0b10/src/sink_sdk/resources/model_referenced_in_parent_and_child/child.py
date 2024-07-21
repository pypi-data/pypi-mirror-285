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
from ...types.model_referenced_in_parent_and_child.model_referenced_in_parent_and_child import (
    ModelReferencedInParentAndChild,
)

__all__ = ["ChildResource", "AsyncChildResource"]


class ChildResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChildResourceWithRawResponse:
        return ChildResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChildResourceWithStreamingResponse:
        return ChildResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelReferencedInParentAndChild:
        return self._get(
            "/model_referenced_in_parent_and_child/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelReferencedInParentAndChild,
        )


class AsyncChildResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChildResourceWithRawResponse:
        return AsyncChildResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChildResourceWithStreamingResponse:
        return AsyncChildResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelReferencedInParentAndChild:
        return await self._get(
            "/model_referenced_in_parent_and_child/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelReferencedInParentAndChild,
        )


class ChildResourceWithRawResponse:
    def __init__(self, child: ChildResource) -> None:
        self._child = child

        self.retrieve = to_raw_response_wrapper(
            child.retrieve,
        )


class AsyncChildResourceWithRawResponse:
    def __init__(self, child: AsyncChildResource) -> None:
        self._child = child

        self.retrieve = async_to_raw_response_wrapper(
            child.retrieve,
        )


class ChildResourceWithStreamingResponse:
    def __init__(self, child: ChildResource) -> None:
        self._child = child

        self.retrieve = to_streamed_response_wrapper(
            child.retrieve,
        )


class AsyncChildResourceWithStreamingResponse:
    def __init__(self, child: AsyncChildResource) -> None:
        self._child = child

        self.retrieve = async_to_streamed_response_wrapper(
            child.retrieve,
        )
