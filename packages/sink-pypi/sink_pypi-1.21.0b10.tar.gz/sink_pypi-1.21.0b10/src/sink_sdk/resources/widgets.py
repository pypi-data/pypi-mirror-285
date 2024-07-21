# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.widget import Widget

__all__ = ["WidgetsResource", "AsyncWidgetsResource"]


class WidgetsResource(SyncAPIResource):
    """
    Widget is love
    Widget is life
    """

    @cached_property
    def with_raw_response(self) -> WidgetsResourceWithRawResponse:
        return WidgetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WidgetsResourceWithStreamingResponse:
        return WidgetsResourceWithStreamingResponse(self)

    def retrieve_with_filter(
        self,
        filter_type: Literal["available", "archived", "out_of_stock"],
        *,
        widget_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Widget:
        """
        Endpoint that tests using an integer and enum in the pathParams

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not filter_type:
            raise ValueError(f"Expected a non-empty value for `filter_type` but received {filter_type!r}")
        return self._get(
            f"/widgets/{widget_id}/filter/{filter_type}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Widget,
        )


class AsyncWidgetsResource(AsyncAPIResource):
    """
    Widget is love
    Widget is life
    """

    @cached_property
    def with_raw_response(self) -> AsyncWidgetsResourceWithRawResponse:
        return AsyncWidgetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWidgetsResourceWithStreamingResponse:
        return AsyncWidgetsResourceWithStreamingResponse(self)

    async def retrieve_with_filter(
        self,
        filter_type: Literal["available", "archived", "out_of_stock"],
        *,
        widget_id: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Widget:
        """
        Endpoint that tests using an integer and enum in the pathParams

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not filter_type:
            raise ValueError(f"Expected a non-empty value for `filter_type` but received {filter_type!r}")
        return await self._get(
            f"/widgets/{widget_id}/filter/{filter_type}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Widget,
        )


class WidgetsResourceWithRawResponse:
    def __init__(self, widgets: WidgetsResource) -> None:
        self._widgets = widgets

        self.retrieve_with_filter = to_raw_response_wrapper(
            widgets.retrieve_with_filter,
        )


class AsyncWidgetsResourceWithRawResponse:
    def __init__(self, widgets: AsyncWidgetsResource) -> None:
        self._widgets = widgets

        self.retrieve_with_filter = async_to_raw_response_wrapper(
            widgets.retrieve_with_filter,
        )


class WidgetsResourceWithStreamingResponse:
    def __init__(self, widgets: WidgetsResource) -> None:
        self._widgets = widgets

        self.retrieve_with_filter = to_streamed_response_wrapper(
            widgets.retrieve_with_filter,
        )


class AsyncWidgetsResourceWithStreamingResponse:
    def __init__(self, widgets: AsyncWidgetsResource) -> None:
        self._widgets = widgets

        self.retrieve_with_filter = async_to_streamed_response_wrapper(
            widgets.retrieve_with_filter,
        )
