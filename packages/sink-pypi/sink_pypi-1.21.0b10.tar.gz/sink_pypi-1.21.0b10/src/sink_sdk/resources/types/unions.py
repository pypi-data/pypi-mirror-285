# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast

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
from ...types.types.union_discriminated_by_property_name_response import UnionDiscriminatedByPropertyNameResponse
from ...types.types.union_discriminated_with_basic_mapping_response import UnionDiscriminatedWithBasicMappingResponse

__all__ = ["UnionsResource", "AsyncUnionsResource"]


class UnionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UnionsResourceWithRawResponse:
        return UnionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UnionsResourceWithStreamingResponse:
        return UnionsResourceWithStreamingResponse(self)

    def discriminated_by_property_name(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UnionDiscriminatedByPropertyNameResponse:
        """
        Endpoint with a response schema that is a discriminated union that just defines
        the `propertyName` config
        """
        return cast(
            UnionDiscriminatedByPropertyNameResponse,
            self._get(
                "/types/unions/discriminated_by_property_name",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, UnionDiscriminatedByPropertyNameResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def discriminated_with_basic_mapping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UnionDiscriminatedWithBasicMappingResponse:
        """
        Endpoint with a response schema that is a discriminated union that also defines
        the `mapping` config
        """
        return cast(
            UnionDiscriminatedWithBasicMappingResponse,
            self._get(
                "/types/unions/discriminated_with_basic_mapping",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, UnionDiscriminatedWithBasicMappingResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncUnionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUnionsResourceWithRawResponse:
        return AsyncUnionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUnionsResourceWithStreamingResponse:
        return AsyncUnionsResourceWithStreamingResponse(self)

    async def discriminated_by_property_name(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UnionDiscriminatedByPropertyNameResponse:
        """
        Endpoint with a response schema that is a discriminated union that just defines
        the `propertyName` config
        """
        return cast(
            UnionDiscriminatedByPropertyNameResponse,
            await self._get(
                "/types/unions/discriminated_by_property_name",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, UnionDiscriminatedByPropertyNameResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def discriminated_with_basic_mapping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UnionDiscriminatedWithBasicMappingResponse:
        """
        Endpoint with a response schema that is a discriminated union that also defines
        the `mapping` config
        """
        return cast(
            UnionDiscriminatedWithBasicMappingResponse,
            await self._get(
                "/types/unions/discriminated_with_basic_mapping",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, UnionDiscriminatedWithBasicMappingResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class UnionsResourceWithRawResponse:
    def __init__(self, unions: UnionsResource) -> None:
        self._unions = unions

        self.discriminated_by_property_name = to_raw_response_wrapper(
            unions.discriminated_by_property_name,
        )
        self.discriminated_with_basic_mapping = to_raw_response_wrapper(
            unions.discriminated_with_basic_mapping,
        )


class AsyncUnionsResourceWithRawResponse:
    def __init__(self, unions: AsyncUnionsResource) -> None:
        self._unions = unions

        self.discriminated_by_property_name = async_to_raw_response_wrapper(
            unions.discriminated_by_property_name,
        )
        self.discriminated_with_basic_mapping = async_to_raw_response_wrapper(
            unions.discriminated_with_basic_mapping,
        )


class UnionsResourceWithStreamingResponse:
    def __init__(self, unions: UnionsResource) -> None:
        self._unions = unions

        self.discriminated_by_property_name = to_streamed_response_wrapper(
            unions.discriminated_by_property_name,
        )
        self.discriminated_with_basic_mapping = to_streamed_response_wrapper(
            unions.discriminated_with_basic_mapping,
        )


class AsyncUnionsResourceWithStreamingResponse:
    def __init__(self, unions: AsyncUnionsResource) -> None:
        self._unions = unions

        self.discriminated_by_property_name = async_to_streamed_response_wrapper(
            unions.discriminated_by_property_name,
        )
        self.discriminated_with_basic_mapping = async_to_streamed_response_wrapper(
            unions.discriminated_with_basic_mapping,
        )
