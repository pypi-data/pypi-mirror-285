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
from ...types.names.openapi_special_used_used_as_property_name_response import (
    OpenAPISpecialUsedUsedAsPropertyNameResponse,
)

__all__ = ["OpenAPISpecialsResource", "AsyncOpenAPISpecialsResource"]


class OpenAPISpecialsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAPISpecialsResourceWithRawResponse:
        return OpenAPISpecialsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAPISpecialsResourceWithStreamingResponse:
        return OpenAPISpecialsResourceWithStreamingResponse(self)

    def used_used_as_property_name(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpenAPISpecialUsedUsedAsPropertyNameResponse:
        return self._get(
            "/names/openapi_specials/used_used_as_property_name",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenAPISpecialUsedUsedAsPropertyNameResponse,
        )


class AsyncOpenAPISpecialsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAPISpecialsResourceWithRawResponse:
        return AsyncOpenAPISpecialsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAPISpecialsResourceWithStreamingResponse:
        return AsyncOpenAPISpecialsResourceWithStreamingResponse(self)

    async def used_used_as_property_name(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpenAPISpecialUsedUsedAsPropertyNameResponse:
        return await self._get(
            "/names/openapi_specials/used_used_as_property_name",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenAPISpecialUsedUsedAsPropertyNameResponse,
        )


class OpenAPISpecialsResourceWithRawResponse:
    def __init__(self, openapi_specials: OpenAPISpecialsResource) -> None:
        self._openapi_specials = openapi_specials

        self.used_used_as_property_name = to_raw_response_wrapper(
            openapi_specials.used_used_as_property_name,
        )


class AsyncOpenAPISpecialsResourceWithRawResponse:
    def __init__(self, openapi_specials: AsyncOpenAPISpecialsResource) -> None:
        self._openapi_specials = openapi_specials

        self.used_used_as_property_name = async_to_raw_response_wrapper(
            openapi_specials.used_used_as_property_name,
        )


class OpenAPISpecialsResourceWithStreamingResponse:
    def __init__(self, openapi_specials: OpenAPISpecialsResource) -> None:
        self._openapi_specials = openapi_specials

        self.used_used_as_property_name = to_streamed_response_wrapper(
            openapi_specials.used_used_as_property_name,
        )


class AsyncOpenAPISpecialsResourceWithStreamingResponse:
    def __init__(self, openapi_specials: AsyncOpenAPISpecialsResource) -> None:
        self._openapi_specials = openapi_specials

        self.used_used_as_property_name = async_to_streamed_response_wrapper(
            openapi_specials.used_used_as_property_name,
        )
