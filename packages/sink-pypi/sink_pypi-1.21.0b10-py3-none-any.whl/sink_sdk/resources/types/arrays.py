# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.types import array_nested_in_params_params
from ..._base_client import make_request_options
from ...types.types.array_float_items_response import ArrayFloatItemsResponse
from ...types.types.array_object_items_response import ArrayObjectItemsResponse

__all__ = ["ArraysResource", "AsyncArraysResource"]


class ArraysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ArraysResourceWithRawResponse:
        return ArraysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ArraysResourceWithStreamingResponse:
        return ArraysResourceWithStreamingResponse(self)

    def float_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArrayFloatItemsResponse:
        """Endpoint with a response schema that is an array of number types."""
        return self._get(
            "/types/array/float_items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ArrayFloatItemsResponse,
        )

    def nested_in_params(
        self,
        *,
        array_param: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a request schema that has a property that points to an array
        model.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/array/model_nested_in_params",
            body=maybe_transform({"array_param": array_param}, array_nested_in_params_params.ArrayNestedInParamsParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def object_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArrayObjectItemsResponse:
        """Endpoint with a response schema that is an array of in-line object types."""
        return self._get(
            "/types/array/object_items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ArrayObjectItemsResponse,
        )


class AsyncArraysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncArraysResourceWithRawResponse:
        return AsyncArraysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncArraysResourceWithStreamingResponse:
        return AsyncArraysResourceWithStreamingResponse(self)

    async def float_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArrayFloatItemsResponse:
        """Endpoint with a response schema that is an array of number types."""
        return await self._get(
            "/types/array/float_items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ArrayFloatItemsResponse,
        )

    async def nested_in_params(
        self,
        *,
        array_param: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a request schema that has a property that points to an array
        model.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/array/model_nested_in_params",
            body=await async_maybe_transform(
                {"array_param": array_param}, array_nested_in_params_params.ArrayNestedInParamsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def object_items(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ArrayObjectItemsResponse:
        """Endpoint with a response schema that is an array of in-line object types."""
        return await self._get(
            "/types/array/object_items",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ArrayObjectItemsResponse,
        )


class ArraysResourceWithRawResponse:
    def __init__(self, arrays: ArraysResource) -> None:
        self._arrays = arrays

        self.float_items = to_raw_response_wrapper(
            arrays.float_items,
        )
        self.nested_in_params = to_raw_response_wrapper(
            arrays.nested_in_params,
        )
        self.object_items = to_raw_response_wrapper(
            arrays.object_items,
        )


class AsyncArraysResourceWithRawResponse:
    def __init__(self, arrays: AsyncArraysResource) -> None:
        self._arrays = arrays

        self.float_items = async_to_raw_response_wrapper(
            arrays.float_items,
        )
        self.nested_in_params = async_to_raw_response_wrapper(
            arrays.nested_in_params,
        )
        self.object_items = async_to_raw_response_wrapper(
            arrays.object_items,
        )


class ArraysResourceWithStreamingResponse:
    def __init__(self, arrays: ArraysResource) -> None:
        self._arrays = arrays

        self.float_items = to_streamed_response_wrapper(
            arrays.float_items,
        )
        self.nested_in_params = to_streamed_response_wrapper(
            arrays.nested_in_params,
        )
        self.object_items = to_streamed_response_wrapper(
            arrays.object_items,
        )


class AsyncArraysResourceWithStreamingResponse:
    def __init__(self, arrays: AsyncArraysResource) -> None:
        self._arrays = arrays

        self.float_items = async_to_streamed_response_wrapper(
            arrays.float_items,
        )
        self.nested_in_params = async_to_streamed_response_wrapper(
            arrays.nested_in_params,
        )
        self.object_items = async_to_streamed_response_wrapper(
            arrays.object_items,
        )
