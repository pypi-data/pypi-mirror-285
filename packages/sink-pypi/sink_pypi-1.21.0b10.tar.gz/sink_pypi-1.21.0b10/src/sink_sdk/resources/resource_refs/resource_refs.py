# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .parent import (
    ParentResource,
    AsyncParentResource,
    ParentResourceWithRawResponse,
    AsyncParentResourceWithRawResponse,
    ParentResourceWithStreamingResponse,
    AsyncParentResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .parent.parent import ParentResource, AsyncParentResource

__all__ = ["ResourceRefsResource", "AsyncResourceRefsResource"]


class ResourceRefsResource(SyncAPIResource):
    @cached_property
    def parent(self) -> ParentResource:
        return ParentResource(self._client)

    @cached_property
    def with_raw_response(self) -> ResourceRefsResourceWithRawResponse:
        return ResourceRefsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResourceRefsResourceWithStreamingResponse:
        return ResourceRefsResourceWithStreamingResponse(self)


class AsyncResourceRefsResource(AsyncAPIResource):
    @cached_property
    def parent(self) -> AsyncParentResource:
        return AsyncParentResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncResourceRefsResourceWithRawResponse:
        return AsyncResourceRefsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResourceRefsResourceWithStreamingResponse:
        return AsyncResourceRefsResourceWithStreamingResponse(self)


class ResourceRefsResourceWithRawResponse:
    def __init__(self, resource_refs: ResourceRefsResource) -> None:
        self._resource_refs = resource_refs

    @cached_property
    def parent(self) -> ParentResourceWithRawResponse:
        return ParentResourceWithRawResponse(self._resource_refs.parent)


class AsyncResourceRefsResourceWithRawResponse:
    def __init__(self, resource_refs: AsyncResourceRefsResource) -> None:
        self._resource_refs = resource_refs

    @cached_property
    def parent(self) -> AsyncParentResourceWithRawResponse:
        return AsyncParentResourceWithRawResponse(self._resource_refs.parent)


class ResourceRefsResourceWithStreamingResponse:
    def __init__(self, resource_refs: ResourceRefsResource) -> None:
        self._resource_refs = resource_refs

    @cached_property
    def parent(self) -> ParentResourceWithStreamingResponse:
        return ParentResourceWithStreamingResponse(self._resource_refs.parent)


class AsyncResourceRefsResourceWithStreamingResponse:
    def __init__(self, resource_refs: AsyncResourceRefsResource) -> None:
        self._resource_refs = resource_refs

    @cached_property
    def parent(self) -> AsyncParentResourceWithStreamingResponse:
        return AsyncParentResourceWithStreamingResponse(self._resource_refs.parent)
