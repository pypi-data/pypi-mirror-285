# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .level_one import (
    LevelOneResource,
    AsyncLevelOneResource,
    LevelOneResourceWithRawResponse,
    AsyncLevelOneResourceWithRawResponse,
    LevelOneResourceWithStreamingResponse,
    AsyncLevelOneResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .level_one.level_one import LevelOneResource, AsyncLevelOneResource

__all__ = ["DeeplyNestedResource", "AsyncDeeplyNestedResource"]


class DeeplyNestedResource(SyncAPIResource):
    @cached_property
    def level_one(self) -> LevelOneResource:
        return LevelOneResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeeplyNestedResourceWithRawResponse:
        return DeeplyNestedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeeplyNestedResourceWithStreamingResponse:
        return DeeplyNestedResourceWithStreamingResponse(self)


class AsyncDeeplyNestedResource(AsyncAPIResource):
    @cached_property
    def level_one(self) -> AsyncLevelOneResource:
        return AsyncLevelOneResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeeplyNestedResourceWithRawResponse:
        return AsyncDeeplyNestedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeeplyNestedResourceWithStreamingResponse:
        return AsyncDeeplyNestedResourceWithStreamingResponse(self)


class DeeplyNestedResourceWithRawResponse:
    def __init__(self, deeply_nested: DeeplyNestedResource) -> None:
        self._deeply_nested = deeply_nested

    @cached_property
    def level_one(self) -> LevelOneResourceWithRawResponse:
        return LevelOneResourceWithRawResponse(self._deeply_nested.level_one)


class AsyncDeeplyNestedResourceWithRawResponse:
    def __init__(self, deeply_nested: AsyncDeeplyNestedResource) -> None:
        self._deeply_nested = deeply_nested

    @cached_property
    def level_one(self) -> AsyncLevelOneResourceWithRawResponse:
        return AsyncLevelOneResourceWithRawResponse(self._deeply_nested.level_one)


class DeeplyNestedResourceWithStreamingResponse:
    def __init__(self, deeply_nested: DeeplyNestedResource) -> None:
        self._deeply_nested = deeply_nested

    @cached_property
    def level_one(self) -> LevelOneResourceWithStreamingResponse:
        return LevelOneResourceWithStreamingResponse(self._deeply_nested.level_one)


class AsyncDeeplyNestedResourceWithStreamingResponse:
    def __init__(self, deeply_nested: AsyncDeeplyNestedResource) -> None:
        self._deeply_nested = deeply_nested

    @cached_property
    def level_one(self) -> AsyncLevelOneResourceWithStreamingResponse:
        return AsyncLevelOneResourceWithStreamingResponse(self._deeply_nested.level_one)
