# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from .....types.names.reserved_names.public.interface import Interface

__all__ = ["InterfaceResource", "AsyncInterfaceResource"]


class InterfaceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InterfaceResourceWithRawResponse:
        return InterfaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InterfaceResourceWithStreamingResponse:
        return InterfaceResourceWithStreamingResponse(self)

    def interface(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Interface:
        return self._get(
            "/names/reserved_names/public/interface",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interface,
        )


class AsyncInterfaceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInterfaceResourceWithRawResponse:
        return AsyncInterfaceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInterfaceResourceWithStreamingResponse:
        return AsyncInterfaceResourceWithStreamingResponse(self)

    async def interface(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Interface:
        return await self._get(
            "/names/reserved_names/public/interface",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Interface,
        )


class InterfaceResourceWithRawResponse:
    def __init__(self, interface: InterfaceResource) -> None:
        self._interface = interface

        self.interface = to_raw_response_wrapper(
            interface.interface,
        )


class AsyncInterfaceResourceWithRawResponse:
    def __init__(self, interface: AsyncInterfaceResource) -> None:
        self._interface = interface

        self.interface = async_to_raw_response_wrapper(
            interface.interface,
        )


class InterfaceResourceWithStreamingResponse:
    def __init__(self, interface: InterfaceResource) -> None:
        self._interface = interface

        self.interface = to_streamed_response_wrapper(
            interface.interface,
        )


class AsyncInterfaceResourceWithStreamingResponse:
    def __init__(self, interface: AsyncInterfaceResource) -> None:
        self._interface = interface

        self.interface = async_to_streamed_response_wrapper(
            interface.interface,
        )
