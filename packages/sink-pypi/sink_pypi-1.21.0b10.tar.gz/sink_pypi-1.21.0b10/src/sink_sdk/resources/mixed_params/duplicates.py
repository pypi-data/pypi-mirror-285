# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from ..._base_client import make_request_options
from ...types.mixed_params import (
    duplicate_body_and_path_params,
    duplicate_query_and_body_params,
    duplicate_query_and_path_params,
)
from ...types.shared.basic_shared_model_object import BasicSharedModelObject

__all__ = ["DuplicatesResource", "AsyncDuplicatesResource"]


class DuplicatesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DuplicatesResourceWithRawResponse:
        return DuplicatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DuplicatesResourceWithStreamingResponse:
        return DuplicatesResourceWithStreamingResponse(self)

    def body_and_path(
        self,
        path_id: str,
        *,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and body params

        Args:
          body_id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/mixed_params/duplicates/body_and_path/{path_id}",
            body=maybe_transform({"id": body_id}, duplicate_body_and_path_params.DuplicateBodyAndPathParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BasicSharedModelObject,
        )

    def query_and_body(
        self,
        *,
        query_id: str,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in query
        and body params

        Args:
          query_id: Query param description

          body_id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/mixed_params/duplicates/query_and_body",
            body=maybe_transform({"id": body_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams),
            ),
            cast_to=BasicSharedModelObject,
        )

    def query_and_path(
        self,
        path_id: str,
        *,
        query_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and query params

        Args:
          query_id: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return self._post(
            f"/mixed_params/duplicates/query_and_path/{path_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"id": query_id}, duplicate_query_and_path_params.DuplicateQueryAndPathParams),
            ),
            cast_to=BasicSharedModelObject,
        )


class AsyncDuplicatesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDuplicatesResourceWithRawResponse:
        return AsyncDuplicatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDuplicatesResourceWithStreamingResponse:
        return AsyncDuplicatesResourceWithStreamingResponse(self)

    async def body_and_path(
        self,
        path_id: str,
        *,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and body params

        Args:
          body_id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/mixed_params/duplicates/body_and_path/{path_id}",
            body=await async_maybe_transform(
                {"id": body_id}, duplicate_body_and_path_params.DuplicateBodyAndPathParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BasicSharedModelObject,
        )

    async def query_and_body(
        self,
        *,
        query_id: str,
        body_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in query
        and body params

        Args:
          query_id: Query param description

          body_id: Body param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/mixed_params/duplicates/query_and_body",
            body=await async_maybe_transform(
                {"id": body_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform(
                    {"id": query_id}, duplicate_query_and_body_params.DuplicateQueryAndBodyParams
                ),
            ),
            cast_to=BasicSharedModelObject,
        )

    async def query_and_path(
        self,
        path_id: str,
        *,
        query_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> BasicSharedModelObject:
        """
        Endpoint with a `requestBody` that defines a param with the same name in path
        and query params

        Args:
          query_id: Query param description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not path_id:
            raise ValueError(f"Expected a non-empty value for `path_id` but received {path_id!r}")
        return await self._post(
            f"/mixed_params/duplicates/query_and_path/{path_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=await async_maybe_transform(
                    {"id": query_id}, duplicate_query_and_path_params.DuplicateQueryAndPathParams
                ),
            ),
            cast_to=BasicSharedModelObject,
        )


class DuplicatesResourceWithRawResponse:
    def __init__(self, duplicates: DuplicatesResource) -> None:
        self._duplicates = duplicates

        self.body_and_path = to_raw_response_wrapper(
            duplicates.body_and_path,
        )
        self.query_and_body = to_raw_response_wrapper(
            duplicates.query_and_body,
        )
        self.query_and_path = to_raw_response_wrapper(
            duplicates.query_and_path,
        )


class AsyncDuplicatesResourceWithRawResponse:
    def __init__(self, duplicates: AsyncDuplicatesResource) -> None:
        self._duplicates = duplicates

        self.body_and_path = async_to_raw_response_wrapper(
            duplicates.body_and_path,
        )
        self.query_and_body = async_to_raw_response_wrapper(
            duplicates.query_and_body,
        )
        self.query_and_path = async_to_raw_response_wrapper(
            duplicates.query_and_path,
        )


class DuplicatesResourceWithStreamingResponse:
    def __init__(self, duplicates: DuplicatesResource) -> None:
        self._duplicates = duplicates

        self.body_and_path = to_streamed_response_wrapper(
            duplicates.body_and_path,
        )
        self.query_and_body = to_streamed_response_wrapper(
            duplicates.query_and_body,
        )
        self.query_and_path = to_streamed_response_wrapper(
            duplicates.query_and_path,
        )


class AsyncDuplicatesResourceWithStreamingResponse:
    def __init__(self, duplicates: AsyncDuplicatesResource) -> None:
        self._duplicates = duplicates

        self.body_and_path = async_to_streamed_response_wrapper(
            duplicates.body_and_path,
        )
        self.query_and_body = async_to_streamed_response_wrapper(
            duplicates.query_and_body,
        )
        self.query_and_path = async_to_streamed_response_wrapper(
            duplicates.query_and_path,
        )
