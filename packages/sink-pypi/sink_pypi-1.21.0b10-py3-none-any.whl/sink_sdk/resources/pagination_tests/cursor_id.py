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
from ...pagination import SyncPageCursorID, AsyncPageCursorID
from ..._base_client import AsyncPaginator, make_request_options
from ...types.my_model import MyModel
from ...types.pagination_tests import cursor_id_list_params

__all__ = ["CursorIDResource", "AsyncCursorIDResource"]


class CursorIDResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CursorIDResourceWithRawResponse:
        return CursorIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CursorIDResourceWithStreamingResponse:
        return CursorIDResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        next_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPageCursorID[MyModel]:
        """
        Test case for cursor_id pagination without a `previous_cursor_param` option.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/cursor_id",
            page=SyncPageCursorID[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "next_id": next_id,
                    },
                    cursor_id_list_params.CursorIDListParams,
                ),
            ),
            model=MyModel,
        )


class AsyncCursorIDResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCursorIDResourceWithRawResponse:
        return AsyncCursorIDResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCursorIDResourceWithStreamingResponse:
        return AsyncCursorIDResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        next_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[MyModel, AsyncPageCursorID[MyModel]]:
        """
        Test case for cursor_id pagination without a `previous_cursor_param` option.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/cursor_id",
            page=AsyncPageCursorID[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "next_id": next_id,
                    },
                    cursor_id_list_params.CursorIDListParams,
                ),
            ),
            model=MyModel,
        )


class CursorIDResourceWithRawResponse:
    def __init__(self, cursor_id: CursorIDResource) -> None:
        self._cursor_id = cursor_id

        self.list = to_raw_response_wrapper(
            cursor_id.list,
        )


class AsyncCursorIDResourceWithRawResponse:
    def __init__(self, cursor_id: AsyncCursorIDResource) -> None:
        self._cursor_id = cursor_id

        self.list = async_to_raw_response_wrapper(
            cursor_id.list,
        )


class CursorIDResourceWithStreamingResponse:
    def __init__(self, cursor_id: CursorIDResource) -> None:
        self._cursor_id = cursor_id

        self.list = to_streamed_response_wrapper(
            cursor_id.list,
        )


class AsyncCursorIDResourceWithStreamingResponse:
    def __init__(self, cursor_id: AsyncCursorIDResource) -> None:
        self._cursor_id = cursor_id

        self.list = async_to_streamed_response_wrapper(
            cursor_id.list,
        )
