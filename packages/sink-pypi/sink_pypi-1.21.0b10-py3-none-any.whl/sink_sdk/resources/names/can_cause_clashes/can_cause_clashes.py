# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .response import (
    ResponseResource,
    AsyncResponseResource,
    ResponseResourceWithRawResponse,
    AsyncResponseResourceWithRawResponse,
    ResponseResourceWithStreamingResponse,
    AsyncResponseResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["CanCauseClashesResource", "AsyncCanCauseClashesResource"]


class CanCauseClashesResource(SyncAPIResource):
    @cached_property
    def response(self) -> ResponseResource:
        """The `Response` class name can cause clashes with imports."""
        return ResponseResource(self._client)

    @cached_property
    def with_raw_response(self) -> CanCauseClashesResourceWithRawResponse:
        return CanCauseClashesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CanCauseClashesResourceWithStreamingResponse:
        return CanCauseClashesResourceWithStreamingResponse(self)


class AsyncCanCauseClashesResource(AsyncAPIResource):
    @cached_property
    def response(self) -> AsyncResponseResource:
        """The `Response` class name can cause clashes with imports."""
        return AsyncResponseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCanCauseClashesResourceWithRawResponse:
        return AsyncCanCauseClashesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCanCauseClashesResourceWithStreamingResponse:
        return AsyncCanCauseClashesResourceWithStreamingResponse(self)


class CanCauseClashesResourceWithRawResponse:
    def __init__(self, can_cause_clashes: CanCauseClashesResource) -> None:
        self._can_cause_clashes = can_cause_clashes

    @cached_property
    def response(self) -> ResponseResourceWithRawResponse:
        """The `Response` class name can cause clashes with imports."""
        return ResponseResourceWithRawResponse(self._can_cause_clashes.response)


class AsyncCanCauseClashesResourceWithRawResponse:
    def __init__(self, can_cause_clashes: AsyncCanCauseClashesResource) -> None:
        self._can_cause_clashes = can_cause_clashes

    @cached_property
    def response(self) -> AsyncResponseResourceWithRawResponse:
        """The `Response` class name can cause clashes with imports."""
        return AsyncResponseResourceWithRawResponse(self._can_cause_clashes.response)


class CanCauseClashesResourceWithStreamingResponse:
    def __init__(self, can_cause_clashes: CanCauseClashesResource) -> None:
        self._can_cause_clashes = can_cause_clashes

    @cached_property
    def response(self) -> ResponseResourceWithStreamingResponse:
        """The `Response` class name can cause clashes with imports."""
        return ResponseResourceWithStreamingResponse(self._can_cause_clashes.response)


class AsyncCanCauseClashesResourceWithStreamingResponse:
    def __init__(self, can_cause_clashes: AsyncCanCauseClashesResource) -> None:
        self._can_cause_clashes = can_cause_clashes

    @cached_property
    def response(self) -> AsyncResponseResourceWithStreamingResponse:
        """The `Response` class name can cause clashes with imports."""
        return AsyncResponseResourceWithStreamingResponse(self._can_cause_clashes.response)
