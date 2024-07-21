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
from ...types.types.write_only_response_simple_response import WriteOnlyResponseSimpleResponse

__all__ = ["WriteOnlyResponsesResource", "AsyncWriteOnlyResponsesResource"]


class WriteOnlyResponsesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WriteOnlyResponsesResourceWithRawResponse:
        return WriteOnlyResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WriteOnlyResponsesResourceWithStreamingResponse:
        return WriteOnlyResponsesResourceWithStreamingResponse(self)

    def simple(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WriteOnlyResponseSimpleResponse:
        """Endpoint with a response schema object that contains a `writeOnly` property."""
        return self._get(
            "/types/write_only_responses/simple",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WriteOnlyResponseSimpleResponse,
        )


class AsyncWriteOnlyResponsesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWriteOnlyResponsesResourceWithRawResponse:
        return AsyncWriteOnlyResponsesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWriteOnlyResponsesResourceWithStreamingResponse:
        return AsyncWriteOnlyResponsesResourceWithStreamingResponse(self)

    async def simple(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WriteOnlyResponseSimpleResponse:
        """Endpoint with a response schema object that contains a `writeOnly` property."""
        return await self._get(
            "/types/write_only_responses/simple",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WriteOnlyResponseSimpleResponse,
        )


class WriteOnlyResponsesResourceWithRawResponse:
    def __init__(self, write_only_responses: WriteOnlyResponsesResource) -> None:
        self._write_only_responses = write_only_responses

        self.simple = to_raw_response_wrapper(
            write_only_responses.simple,
        )


class AsyncWriteOnlyResponsesResourceWithRawResponse:
    def __init__(self, write_only_responses: AsyncWriteOnlyResponsesResource) -> None:
        self._write_only_responses = write_only_responses

        self.simple = async_to_raw_response_wrapper(
            write_only_responses.simple,
        )


class WriteOnlyResponsesResourceWithStreamingResponse:
    def __init__(self, write_only_responses: WriteOnlyResponsesResource) -> None:
        self._write_only_responses = write_only_responses

        self.simple = to_streamed_response_wrapper(
            write_only_responses.simple,
        )


class AsyncWriteOnlyResponsesResourceWithStreamingResponse:
    def __init__(self, write_only_responses: AsyncWriteOnlyResponsesResource) -> None:
        self._write_only_responses = write_only_responses

        self.simple = async_to_streamed_response_wrapper(
            write_only_responses.simple,
        )
