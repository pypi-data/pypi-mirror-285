# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import empty_body_typed_params_params, empty_body_stainless_empty_object_params
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
from ..types.shared.basic_shared_model_object import BasicSharedModelObject

__all__ = ["EmptyBodyResource", "AsyncEmptyBodyResource"]


class EmptyBodyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EmptyBodyResourceWithRawResponse:
        return EmptyBodyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EmptyBodyResourceWithStreamingResponse:
        return EmptyBodyResourceWithStreamingResponse(self)

    def stainless_empty_object(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        body: empty_body_stainless_empty_object_params.Body,
        query_param: str | NotGiven = NOT_GIVEN,
        second_query_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with x-stainless-empty-object should still have types for params

        Args:
          query_param: Query param description

          second_query_param: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_param:
            raise ValueError(f"Expected a non-empty value for `path_param` but received {path_param!r}")
        return self._post(
            f"/mixed_params/with_empty_body/{path_param}/x_stainless_empty_object",
            body=maybe_transform(body, empty_body_stainless_empty_object_params.EmptyBodyStainlessEmptyObjectParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {
                        "query_param": query_param,
                        "second_query_param": second_query_param,
                    },
                    empty_body_stainless_empty_object_params.EmptyBodyStainlessEmptyObjectParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )

    def typed_params(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        body: object,
        query_param: str | NotGiven = NOT_GIVEN,
        second_query_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with an empty `requestBody` should still have types for params

        Args:
          query_param: Query param description

          second_query_param: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_param:
            raise ValueError(f"Expected a non-empty value for `path_param` but received {path_param!r}")
        return self._post(
            f"/mixed_params/with_empty_body/{path_param}",
            body=maybe_transform(body, empty_body_typed_params_params.EmptyBodyTypedParamsParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform(
                    {
                        "query_param": query_param,
                        "second_query_param": second_query_param,
                    },
                    empty_body_typed_params_params.EmptyBodyTypedParamsParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )


class AsyncEmptyBodyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEmptyBodyResourceWithRawResponse:
        return AsyncEmptyBodyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEmptyBodyResourceWithStreamingResponse:
        return AsyncEmptyBodyResourceWithStreamingResponse(self)

    async def stainless_empty_object(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        body: empty_body_stainless_empty_object_params.Body,
        query_param: str | NotGiven = NOT_GIVEN,
        second_query_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with x-stainless-empty-object should still have types for params

        Args:
          query_param: Query param description

          second_query_param: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_param:
            raise ValueError(f"Expected a non-empty value for `path_param` but received {path_param!r}")
        return await self._post(
            f"/mixed_params/with_empty_body/{path_param}/x_stainless_empty_object",
            body=await async_maybe_transform(
                body, empty_body_stainless_empty_object_params.EmptyBodyStainlessEmptyObjectParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform(
                    {
                        "query_param": query_param,
                        "second_query_param": second_query_param,
                    },
                    empty_body_stainless_empty_object_params.EmptyBodyStainlessEmptyObjectParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )

    async def typed_params(
        self,
        path_param: str | NotGiven = NOT_GIVEN,
        *,
        body: object,
        query_param: str | NotGiven = NOT_GIVEN,
        second_query_param: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with an empty `requestBody` should still have types for params

        Args:
          query_param: Query param description

          second_query_param: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_param:
            raise ValueError(f"Expected a non-empty value for `path_param` but received {path_param!r}")
        return await self._post(
            f"/mixed_params/with_empty_body/{path_param}",
            body=await async_maybe_transform(body, empty_body_typed_params_params.EmptyBodyTypedParamsParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform(
                    {
                        "query_param": query_param,
                        "second_query_param": second_query_param,
                    },
                    empty_body_typed_params_params.EmptyBodyTypedParamsParams,
                ),
            ),
            cast_to=BasicSharedModelObject,
        )


class EmptyBodyResourceWithRawResponse:
    def __init__(self, empty_body: EmptyBodyResource) -> None:
        self._empty_body = empty_body

        self.stainless_empty_object = to_raw_response_wrapper(
            empty_body.stainless_empty_object,
        )
        self.typed_params = to_raw_response_wrapper(
            empty_body.typed_params,
        )


class AsyncEmptyBodyResourceWithRawResponse:
    def __init__(self, empty_body: AsyncEmptyBodyResource) -> None:
        self._empty_body = empty_body

        self.stainless_empty_object = async_to_raw_response_wrapper(
            empty_body.stainless_empty_object,
        )
        self.typed_params = async_to_raw_response_wrapper(
            empty_body.typed_params,
        )


class EmptyBodyResourceWithStreamingResponse:
    def __init__(self, empty_body: EmptyBodyResource) -> None:
        self._empty_body = empty_body

        self.stainless_empty_object = to_streamed_response_wrapper(
            empty_body.stainless_empty_object,
        )
        self.typed_params = to_streamed_response_wrapper(
            empty_body.typed_params,
        )


class AsyncEmptyBodyResourceWithStreamingResponse:
    def __init__(self, empty_body: AsyncEmptyBodyResource) -> None:
        self._empty_body = empty_body

        self.stainless_empty_object = async_to_streamed_response_wrapper(
            empty_body.stainless_empty_object,
        )
        self.typed_params = async_to_streamed_response_wrapper(
            empty_body.typed_params,
        )
