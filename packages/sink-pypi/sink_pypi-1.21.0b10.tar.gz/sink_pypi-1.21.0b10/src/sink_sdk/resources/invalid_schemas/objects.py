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
from ...types.invalid_schemas.object_missing_items_response import ObjectMissingItemsResponse

__all__ = ["ObjectsResource", "AsyncObjectsResource"]


class ObjectsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ObjectsResourceWithRawResponse:
        return ObjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ObjectsResourceWithStreamingResponse:
        return ObjectsResourceWithStreamingResponse(self)

    def missing_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMissingItemsResponse:
        return self._get(
            "/invalid_schemas/objects/property_missing_def",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMissingItemsResponse,
        )


class AsyncObjectsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncObjectsResourceWithRawResponse:
        return AsyncObjectsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncObjectsResourceWithStreamingResponse:
        return AsyncObjectsResourceWithStreamingResponse(self)

    async def missing_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ObjectMissingItemsResponse:
        return await self._get(
            "/invalid_schemas/objects/property_missing_def",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ObjectMissingItemsResponse,
        )


class ObjectsResourceWithRawResponse:
    def __init__(self, objects: ObjectsResource) -> None:
        self._objects = objects

        self.missing_items = to_raw_response_wrapper(
            objects.missing_items,
        )


class AsyncObjectsResourceWithRawResponse:
    def __init__(self, objects: AsyncObjectsResource) -> None:
        self._objects = objects

        self.missing_items = async_to_raw_response_wrapper(
            objects.missing_items,
        )


class ObjectsResourceWithStreamingResponse:
    def __init__(self, objects: ObjectsResource) -> None:
        self._objects = objects

        self.missing_items = to_streamed_response_wrapper(
            objects.missing_items,
        )


class AsyncObjectsResourceWithStreamingResponse:
    def __init__(self, objects: AsyncObjectsResource) -> None:
        self._objects = objects

        self.missing_items = async_to_streamed_response_wrapper(
            objects.missing_items,
        )
