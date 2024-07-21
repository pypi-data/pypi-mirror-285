# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncPageCursorTopLevelArray, AsyncPageCursorTopLevelArray
from ..._base_client import AsyncPaginator, make_request_options
from ...types.my_model import MyModel
from ...types.pagination_tests import top_level_array_basic_cursor_params

__all__ = ["TopLevelArraysResource", "AsyncTopLevelArraysResource"]


class TopLevelArraysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TopLevelArraysResourceWithRawResponse:
        return TopLevelArraysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TopLevelArraysResourceWithStreamingResponse:
        return TopLevelArraysResourceWithStreamingResponse(self)

    def basic_cursor(
        self,
        *,
        cursor: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPageCursorTopLevelArray[MyModel]:
        """
        Test case for top level arrays with cursor pagination

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/top_level_arrays/basic_cursor",
            page=SyncPageCursorTopLevelArray[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    top_level_array_basic_cursor_params.TopLevelArrayBasicCursorParams,
                ),
            ),
            model=MyModel,
        )


class AsyncTopLevelArraysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTopLevelArraysResourceWithRawResponse:
        return AsyncTopLevelArraysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTopLevelArraysResourceWithStreamingResponse:
        return AsyncTopLevelArraysResourceWithStreamingResponse(self)

    def basic_cursor(
        self,
        *,
        cursor: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[MyModel, AsyncPageCursorTopLevelArray[MyModel]]:
        """
        Test case for top level arrays with cursor pagination

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/top_level_arrays/basic_cursor",
            page=AsyncPageCursorTopLevelArray[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    top_level_array_basic_cursor_params.TopLevelArrayBasicCursorParams,
                ),
            ),
            model=MyModel,
        )


class TopLevelArraysResourceWithRawResponse:
    def __init__(self, top_level_arrays: TopLevelArraysResource) -> None:
        self._top_level_arrays = top_level_arrays

        self.basic_cursor = to_raw_response_wrapper(
            top_level_arrays.basic_cursor,
        )


class AsyncTopLevelArraysResourceWithRawResponse:
    def __init__(self, top_level_arrays: AsyncTopLevelArraysResource) -> None:
        self._top_level_arrays = top_level_arrays

        self.basic_cursor = async_to_raw_response_wrapper(
            top_level_arrays.basic_cursor,
        )


class TopLevelArraysResourceWithStreamingResponse:
    def __init__(self, top_level_arrays: TopLevelArraysResource) -> None:
        self._top_level_arrays = top_level_arrays

        self.basic_cursor = to_streamed_response_wrapper(
            top_level_arrays.basic_cursor,
        )


class AsyncTopLevelArraysResourceWithStreamingResponse:
    def __init__(self, top_level_arrays: AsyncTopLevelArraysResource) -> None:
        self._top_level_arrays = top_level_arrays

        self.basic_cursor = async_to_streamed_response_wrapper(
            top_level_arrays.basic_cursor,
        )
