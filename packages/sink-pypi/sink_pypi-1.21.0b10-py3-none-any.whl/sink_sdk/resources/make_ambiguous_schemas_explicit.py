# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ..types.make_ambiguous_schemas_explicit_make_ambiguous_schemas_explicit_response import (
    MakeAmbiguousSchemasExplicitMakeAmbiguousSchemasExplicitResponse,
)

__all__ = ["MakeAmbiguousSchemasExplicitResource", "AsyncMakeAmbiguousSchemasExplicitResource"]


class MakeAmbiguousSchemasExplicitResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MakeAmbiguousSchemasExplicitResourceWithRawResponse:
        return MakeAmbiguousSchemasExplicitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MakeAmbiguousSchemasExplicitResourceWithStreamingResponse:
        return MakeAmbiguousSchemasExplicitResourceWithStreamingResponse(self)

    def make_ambiguous_schemas_explicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MakeAmbiguousSchemasExplicitMakeAmbiguousSchemasExplicitResponse:
        """Test case for makeAmbiguousSchemasExplicit"""
        return self._get(
            "/make-ambiguous-schemas-explicit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MakeAmbiguousSchemasExplicitMakeAmbiguousSchemasExplicitResponse,
        )


class AsyncMakeAmbiguousSchemasExplicitResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMakeAmbiguousSchemasExplicitResourceWithRawResponse:
        return AsyncMakeAmbiguousSchemasExplicitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMakeAmbiguousSchemasExplicitResourceWithStreamingResponse:
        return AsyncMakeAmbiguousSchemasExplicitResourceWithStreamingResponse(self)

    async def make_ambiguous_schemas_explicit(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MakeAmbiguousSchemasExplicitMakeAmbiguousSchemasExplicitResponse:
        """Test case for makeAmbiguousSchemasExplicit"""
        return await self._get(
            "/make-ambiguous-schemas-explicit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MakeAmbiguousSchemasExplicitMakeAmbiguousSchemasExplicitResponse,
        )


class MakeAmbiguousSchemasExplicitResourceWithRawResponse:
    def __init__(self, make_ambiguous_schemas_explicit: MakeAmbiguousSchemasExplicitResource) -> None:
        self._make_ambiguous_schemas_explicit = make_ambiguous_schemas_explicit

        self.make_ambiguous_schemas_explicit = to_raw_response_wrapper(
            make_ambiguous_schemas_explicit.make_ambiguous_schemas_explicit,
        )


class AsyncMakeAmbiguousSchemasExplicitResourceWithRawResponse:
    def __init__(self, make_ambiguous_schemas_explicit: AsyncMakeAmbiguousSchemasExplicitResource) -> None:
        self._make_ambiguous_schemas_explicit = make_ambiguous_schemas_explicit

        self.make_ambiguous_schemas_explicit = async_to_raw_response_wrapper(
            make_ambiguous_schemas_explicit.make_ambiguous_schemas_explicit,
        )


class MakeAmbiguousSchemasExplicitResourceWithStreamingResponse:
    def __init__(self, make_ambiguous_schemas_explicit: MakeAmbiguousSchemasExplicitResource) -> None:
        self._make_ambiguous_schemas_explicit = make_ambiguous_schemas_explicit

        self.make_ambiguous_schemas_explicit = to_streamed_response_wrapper(
            make_ambiguous_schemas_explicit.make_ambiguous_schemas_explicit,
        )


class AsyncMakeAmbiguousSchemasExplicitResourceWithStreamingResponse:
    def __init__(self, make_ambiguous_schemas_explicit: AsyncMakeAmbiguousSchemasExplicitResource) -> None:
        self._make_ambiguous_schemas_explicit = make_ambiguous_schemas_explicit

        self.make_ambiguous_schemas_explicit = async_to_streamed_response_wrapper(
            make_ambiguous_schemas_explicit.make_ambiguous_schemas_explicit,
        )
