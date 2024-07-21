# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .class_ import (
    ClassResource,
    AsyncClassResource,
    ClassResourceWithRawResponse,
    AsyncClassResourceWithRawResponse,
    ClassResourceWithStreamingResponse,
    AsyncClassResourceWithStreamingResponse,
)
from .private import (
    PrivateResource,
    AsyncPrivateResource,
    PrivateResourceWithRawResponse,
    AsyncPrivateResourceWithRawResponse,
    PrivateResourceWithStreamingResponse,
    AsyncPrivateResourceWithStreamingResponse,
)
from .interface import (
    InterfaceResource,
    AsyncInterfaceResource,
    InterfaceResourceWithRawResponse,
    AsyncInterfaceResourceWithRawResponse,
    InterfaceResourceWithStreamingResponse,
    AsyncInterfaceResourceWithStreamingResponse,
)
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.names.reserved_names.public.public import Public

__all__ = ["PublicResource", "AsyncPublicResource"]


class PublicResource(SyncAPIResource):
    @cached_property
    def private(self) -> PrivateResource:
        return PrivateResource(self._client)

    @cached_property
    def interface(self) -> InterfaceResource:
        return InterfaceResource(self._client)

    @cached_property
    def class_(self) -> ClassResource:
        return ClassResource(self._client)

    @cached_property
    def with_raw_response(self) -> PublicResourceWithRawResponse:
        return PublicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PublicResourceWithStreamingResponse:
        return PublicResourceWithStreamingResponse(self)

    def public(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Public:
        return self._get(
            "/names/reserved_names/public",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Public,
        )


class AsyncPublicResource(AsyncAPIResource):
    @cached_property
    def private(self) -> AsyncPrivateResource:
        return AsyncPrivateResource(self._client)

    @cached_property
    def interface(self) -> AsyncInterfaceResource:
        return AsyncInterfaceResource(self._client)

    @cached_property
    def class_(self) -> AsyncClassResource:
        return AsyncClassResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPublicResourceWithRawResponse:
        return AsyncPublicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPublicResourceWithStreamingResponse:
        return AsyncPublicResourceWithStreamingResponse(self)

    async def public(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Public:
        return await self._get(
            "/names/reserved_names/public",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Public,
        )


class PublicResourceWithRawResponse:
    def __init__(self, public: PublicResource) -> None:
        self._public = public

        self.public = to_raw_response_wrapper(
            public.public,
        )

    @cached_property
    def private(self) -> PrivateResourceWithRawResponse:
        return PrivateResourceWithRawResponse(self._public.private)

    @cached_property
    def interface(self) -> InterfaceResourceWithRawResponse:
        return InterfaceResourceWithRawResponse(self._public.interface)

    @cached_property
    def class_(self) -> ClassResourceWithRawResponse:
        return ClassResourceWithRawResponse(self._public.class_)


class AsyncPublicResourceWithRawResponse:
    def __init__(self, public: AsyncPublicResource) -> None:
        self._public = public

        self.public = async_to_raw_response_wrapper(
            public.public,
        )

    @cached_property
    def private(self) -> AsyncPrivateResourceWithRawResponse:
        return AsyncPrivateResourceWithRawResponse(self._public.private)

    @cached_property
    def interface(self) -> AsyncInterfaceResourceWithRawResponse:
        return AsyncInterfaceResourceWithRawResponse(self._public.interface)

    @cached_property
    def class_(self) -> AsyncClassResourceWithRawResponse:
        return AsyncClassResourceWithRawResponse(self._public.class_)


class PublicResourceWithStreamingResponse:
    def __init__(self, public: PublicResource) -> None:
        self._public = public

        self.public = to_streamed_response_wrapper(
            public.public,
        )

    @cached_property
    def private(self) -> PrivateResourceWithStreamingResponse:
        return PrivateResourceWithStreamingResponse(self._public.private)

    @cached_property
    def interface(self) -> InterfaceResourceWithStreamingResponse:
        return InterfaceResourceWithStreamingResponse(self._public.interface)

    @cached_property
    def class_(self) -> ClassResourceWithStreamingResponse:
        return ClassResourceWithStreamingResponse(self._public.class_)


class AsyncPublicResourceWithStreamingResponse:
    def __init__(self, public: AsyncPublicResource) -> None:
        self._public = public

        self.public = async_to_streamed_response_wrapper(
            public.public,
        )

    @cached_property
    def private(self) -> AsyncPrivateResourceWithStreamingResponse:
        return AsyncPrivateResourceWithStreamingResponse(self._public.private)

    @cached_property
    def interface(self) -> AsyncInterfaceResourceWithStreamingResponse:
        return AsyncInterfaceResourceWithStreamingResponse(self._public.interface)

    @cached_property
    def class_(self) -> AsyncClassResourceWithStreamingResponse:
        return AsyncClassResourceWithStreamingResponse(self._public.class_)
