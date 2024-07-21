# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.names.reserved_names.public.class_ import Class

__all__ = ["ClassResource", "AsyncClassResource"]


class ClassResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassResourceWithRawResponse:
        return ClassResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassResourceWithStreamingResponse:
        return ClassResourceWithStreamingResponse(self)

    def class_(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Class:
        return self._get(
            "/names/reserved_names/public/class",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Class,
        )


class AsyncClassResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassResourceWithRawResponse:
        return AsyncClassResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassResourceWithStreamingResponse:
        return AsyncClassResourceWithStreamingResponse(self)

    async def class_(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Class:
        return await self._get(
            "/names/reserved_names/public/class",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Class,
        )


class ClassResourceWithRawResponse:
    def __init__(self, class_: ClassResource) -> None:
        self._class_ = class_

        self.class_ = to_raw_response_wrapper(
            class_.class_,
        )


class AsyncClassResourceWithRawResponse:
    def __init__(self, class_: AsyncClassResource) -> None:
        self._class_ = class_

        self.class_ = async_to_raw_response_wrapper(
            class_.class_,
        )


class ClassResourceWithStreamingResponse:
    def __init__(self, class_: ClassResource) -> None:
        self._class_ = class_

        self.class_ = to_streamed_response_wrapper(
            class_.class_,
        )


class AsyncClassResourceWithStreamingResponse:
    def __init__(self, class_: AsyncClassResource) -> None:
        self._class_ = class_

        self.class_ = async_to_streamed_response_wrapper(
            class_.class_,
        )
