# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .eeoc import (
    EEOCResource,
    AsyncEEOCResource,
    EEOCResourceWithRawResponse,
    AsyncEEOCResourceWithRawResponse,
    EEOCResourceWithStreamingResponse,
    AsyncEEOCResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["CasingResource", "AsyncCasingResource"]


class CasingResource(SyncAPIResource):
    @cached_property
    def eeoc(self) -> EEOCResource:
        return EEOCResource(self._client)

    @cached_property
    def with_raw_response(self) -> CasingResourceWithRawResponse:
        return CasingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CasingResourceWithStreamingResponse:
        return CasingResourceWithStreamingResponse(self)


class AsyncCasingResource(AsyncAPIResource):
    @cached_property
    def eeoc(self) -> AsyncEEOCResource:
        return AsyncEEOCResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCasingResourceWithRawResponse:
        return AsyncCasingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCasingResourceWithStreamingResponse:
        return AsyncCasingResourceWithStreamingResponse(self)


class CasingResourceWithRawResponse:
    def __init__(self, casing: CasingResource) -> None:
        self._casing = casing

    @cached_property
    def eeoc(self) -> EEOCResourceWithRawResponse:
        return EEOCResourceWithRawResponse(self._casing.eeoc)


class AsyncCasingResourceWithRawResponse:
    def __init__(self, casing: AsyncCasingResource) -> None:
        self._casing = casing

    @cached_property
    def eeoc(self) -> AsyncEEOCResourceWithRawResponse:
        return AsyncEEOCResourceWithRawResponse(self._casing.eeoc)


class CasingResourceWithStreamingResponse:
    def __init__(self, casing: CasingResource) -> None:
        self._casing = casing

    @cached_property
    def eeoc(self) -> EEOCResourceWithStreamingResponse:
        return EEOCResourceWithStreamingResponse(self._casing.eeoc)


class AsyncCasingResourceWithStreamingResponse:
    def __init__(self, casing: AsyncCasingResource) -> None:
        self._casing = casing

    @cached_property
    def eeoc(self) -> AsyncEEOCResourceWithStreamingResponse:
        return AsyncEEOCResourceWithStreamingResponse(self._casing.eeoc)
