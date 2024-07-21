# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import (
    openapi_format_array_type_one_entry_params,
    openapi_format_array_type_one_entry_with_null_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.openapi_format_array_type_one_entry_response import OpenAPIFormatArrayTypeOneEntryResponse
from ..types.openapi_format_array_type_one_entry_with_null_response import (
    OpenAPIFormatArrayTypeOneEntryWithNullResponse,
)

__all__ = ["OpenAPIFormatsResource", "AsyncOpenAPIFormatsResource"]


class OpenAPIFormatsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAPIFormatsResourceWithRawResponse:
        return OpenAPIFormatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAPIFormatsResourceWithStreamingResponse:
        return OpenAPIFormatsResourceWithStreamingResponse(self)

    def array_type_one_entry(
        self,
        *,
        enable_debug_logging: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> OpenAPIFormatArrayTypeOneEntryResponse:
        """
        See https://linear.app/stainless/issue/STA-569/support-for-type-[object-null]

        Args:
          enable_debug_logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/openapi_formats/array_type_one_entry",
            body=maybe_transform(
                {"enable_debug_logging": enable_debug_logging},
                openapi_format_array_type_one_entry_params.OpenAPIFormatArrayTypeOneEntryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=OpenAPIFormatArrayTypeOneEntryResponse,
        )

    def array_type_one_entry_with_null(
        self,
        *,
        enable_debug_logging: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Optional[OpenAPIFormatArrayTypeOneEntryWithNullResponse]:
        """
        The `type` property being set to [T, null] should result in an optional response
        return type in generated SDKs.

        See https://linear.app/stainless/issue/STA-569/support-for-type-[object-null]

        Args:
          enable_debug_logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/openapi_formats/array_type_one_entry_with_null",
            body=maybe_transform(
                {"enable_debug_logging": enable_debug_logging},
                openapi_format_array_type_one_entry_with_null_params.OpenAPIFormatArrayTypeOneEntryWithNullParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=OpenAPIFormatArrayTypeOneEntryWithNullResponse,
        )


class AsyncOpenAPIFormatsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAPIFormatsResourceWithRawResponse:
        return AsyncOpenAPIFormatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAPIFormatsResourceWithStreamingResponse:
        return AsyncOpenAPIFormatsResourceWithStreamingResponse(self)

    async def array_type_one_entry(
        self,
        *,
        enable_debug_logging: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> OpenAPIFormatArrayTypeOneEntryResponse:
        """
        See https://linear.app/stainless/issue/STA-569/support-for-type-[object-null]

        Args:
          enable_debug_logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/openapi_formats/array_type_one_entry",
            body=await async_maybe_transform(
                {"enable_debug_logging": enable_debug_logging},
                openapi_format_array_type_one_entry_params.OpenAPIFormatArrayTypeOneEntryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=OpenAPIFormatArrayTypeOneEntryResponse,
        )

    async def array_type_one_entry_with_null(
        self,
        *,
        enable_debug_logging: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Optional[OpenAPIFormatArrayTypeOneEntryWithNullResponse]:
        """
        The `type` property being set to [T, null] should result in an optional response
        return type in generated SDKs.

        See https://linear.app/stainless/issue/STA-569/support-for-type-[object-null]

        Args:
          enable_debug_logging

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/openapi_formats/array_type_one_entry_with_null",
            body=await async_maybe_transform(
                {"enable_debug_logging": enable_debug_logging},
                openapi_format_array_type_one_entry_with_null_params.OpenAPIFormatArrayTypeOneEntryWithNullParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=OpenAPIFormatArrayTypeOneEntryWithNullResponse,
        )


class OpenAPIFormatsResourceWithRawResponse:
    def __init__(self, openapi_formats: OpenAPIFormatsResource) -> None:
        self._openapi_formats = openapi_formats

        self.array_type_one_entry = to_raw_response_wrapper(
            openapi_formats.array_type_one_entry,
        )
        self.array_type_one_entry_with_null = to_raw_response_wrapper(
            openapi_formats.array_type_one_entry_with_null,
        )


class AsyncOpenAPIFormatsResourceWithRawResponse:
    def __init__(self, openapi_formats: AsyncOpenAPIFormatsResource) -> None:
        self._openapi_formats = openapi_formats

        self.array_type_one_entry = async_to_raw_response_wrapper(
            openapi_formats.array_type_one_entry,
        )
        self.array_type_one_entry_with_null = async_to_raw_response_wrapper(
            openapi_formats.array_type_one_entry_with_null,
        )


class OpenAPIFormatsResourceWithStreamingResponse:
    def __init__(self, openapi_formats: OpenAPIFormatsResource) -> None:
        self._openapi_formats = openapi_formats

        self.array_type_one_entry = to_streamed_response_wrapper(
            openapi_formats.array_type_one_entry,
        )
        self.array_type_one_entry_with_null = to_streamed_response_wrapper(
            openapi_formats.array_type_one_entry_with_null,
        )


class AsyncOpenAPIFormatsResourceWithStreamingResponse:
    def __init__(self, openapi_formats: AsyncOpenAPIFormatsResource) -> None:
        self._openapi_formats = openapi_formats

        self.array_type_one_entry = async_to_streamed_response_wrapper(
            openapi_formats.array_type_one_entry,
        )
        self.array_type_one_entry_with_null = async_to_streamed_response_wrapper(
            openapi_formats.array_type_one_entry_with_null,
        )
