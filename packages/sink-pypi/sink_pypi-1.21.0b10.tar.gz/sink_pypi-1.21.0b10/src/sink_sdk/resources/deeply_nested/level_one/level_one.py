# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .level_two import (
    LevelTwoResource,
    AsyncLevelTwoResource,
    LevelTwoResourceWithRawResponse,
    AsyncLevelTwoResourceWithRawResponse,
    LevelTwoResourceWithStreamingResponse,
    AsyncLevelTwoResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.card import Card
from ...._base_client import make_request_options
from .level_two.level_two import LevelTwoResource, AsyncLevelTwoResource

__all__ = ["LevelOneResource", "AsyncLevelOneResource"]


class LevelOneResource(SyncAPIResource):
    @cached_property
    def level_two(self) -> LevelTwoResource:
        return LevelTwoResource(self._client)

    @cached_property
    def with_raw_response(self) -> LevelOneResourceWithRawResponse:
        return LevelOneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LevelOneResourceWithStreamingResponse:
        return LevelOneResourceWithStreamingResponse(self)

    def method_level_1(
        self,
        card_token: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Card:
        """
        Get card configuration such as spend limit and state.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not card_token:
            raise ValueError(f"Expected a non-empty value for `card_token` but received {card_token!r}")
        return self._get(
            f"/cards/{card_token}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Card,
        )


class AsyncLevelOneResource(AsyncAPIResource):
    @cached_property
    def level_two(self) -> AsyncLevelTwoResource:
        return AsyncLevelTwoResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLevelOneResourceWithRawResponse:
        return AsyncLevelOneResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLevelOneResourceWithStreamingResponse:
        return AsyncLevelOneResourceWithStreamingResponse(self)

    async def method_level_1(
        self,
        card_token: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Card:
        """
        Get card configuration such as spend limit and state.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not card_token:
            raise ValueError(f"Expected a non-empty value for `card_token` but received {card_token!r}")
        return await self._get(
            f"/cards/{card_token}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Card,
        )


class LevelOneResourceWithRawResponse:
    def __init__(self, level_one: LevelOneResource) -> None:
        self._level_one = level_one

        self.method_level_1 = to_raw_response_wrapper(
            level_one.method_level_1,
        )

    @cached_property
    def level_two(self) -> LevelTwoResourceWithRawResponse:
        return LevelTwoResourceWithRawResponse(self._level_one.level_two)


class AsyncLevelOneResourceWithRawResponse:
    def __init__(self, level_one: AsyncLevelOneResource) -> None:
        self._level_one = level_one

        self.method_level_1 = async_to_raw_response_wrapper(
            level_one.method_level_1,
        )

    @cached_property
    def level_two(self) -> AsyncLevelTwoResourceWithRawResponse:
        return AsyncLevelTwoResourceWithRawResponse(self._level_one.level_two)


class LevelOneResourceWithStreamingResponse:
    def __init__(self, level_one: LevelOneResource) -> None:
        self._level_one = level_one

        self.method_level_1 = to_streamed_response_wrapper(
            level_one.method_level_1,
        )

    @cached_property
    def level_two(self) -> LevelTwoResourceWithStreamingResponse:
        return LevelTwoResourceWithStreamingResponse(self._level_one.level_two)


class AsyncLevelOneResourceWithStreamingResponse:
    def __init__(self, level_one: AsyncLevelOneResource) -> None:
        self._level_one = level_one

        self.method_level_1 = async_to_streamed_response_wrapper(
            level_one.method_level_1,
        )

    @cached_property
    def level_two(self) -> AsyncLevelTwoResourceWithStreamingResponse:
        return AsyncLevelTwoResourceWithStreamingResponse(self._level_one.level_two)
