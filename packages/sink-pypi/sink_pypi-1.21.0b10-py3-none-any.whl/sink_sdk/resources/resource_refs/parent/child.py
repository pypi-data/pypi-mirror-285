# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.resource_refs.parent.child_model import ChildModel

__all__ = ["ChildResource", "AsyncChildResource"]


class ChildResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChildResourceWithRawResponse:
        return ChildResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChildResourceWithStreamingResponse:
        return ChildResourceWithStreamingResponse(self)

    def returns_child_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChildModel:
        """
        endpoint that returns a model that is referenced from a model in a parent
        resource
        """
        return self._get(
            "/resource_refs/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChildModel,
        )


class AsyncChildResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChildResourceWithRawResponse:
        return AsyncChildResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChildResourceWithStreamingResponse:
        return AsyncChildResourceWithStreamingResponse(self)

    async def returns_child_model(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChildModel:
        """
        endpoint that returns a model that is referenced from a model in a parent
        resource
        """
        return await self._get(
            "/resource_refs/child",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChildModel,
        )


class ChildResourceWithRawResponse:
    def __init__(self, child: ChildResource) -> None:
        self._child = child

        self.returns_child_model = to_raw_response_wrapper(
            child.returns_child_model,
        )


class AsyncChildResourceWithRawResponse:
    def __init__(self, child: AsyncChildResource) -> None:
        self._child = child

        self.returns_child_model = async_to_raw_response_wrapper(
            child.returns_child_model,
        )


class ChildResourceWithStreamingResponse:
    def __init__(self, child: ChildResource) -> None:
        self._child = child

        self.returns_child_model = to_streamed_response_wrapper(
            child.returns_child_model,
        )


class AsyncChildResourceWithStreamingResponse:
    def __init__(self, child: AsyncChildResource) -> None:
        self._child = child

        self.returns_child_model = async_to_streamed_response_wrapper(
            child.returns_child_model,
        )
