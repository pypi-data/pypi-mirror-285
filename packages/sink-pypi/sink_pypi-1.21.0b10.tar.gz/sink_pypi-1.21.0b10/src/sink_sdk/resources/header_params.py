# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import header_param_all_types_params, header_param_client_argument_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import (
    is_given,
    maybe_transform,
    strip_not_given,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["HeaderParamsResource", "AsyncHeaderParamsResource"]


class HeaderParamsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HeaderParamsResourceWithRawResponse:
        return HeaderParamsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HeaderParamsResourceWithStreamingResponse:
        return HeaderParamsResourceWithStreamingResponse(self)

    def all_types(
        self,
        *,
        x_required_boolean: bool,
        x_required_integer: int,
        x_required_number: float,
        x_required_string: str,
        body_argument: str | NotGiven = NOT_GIVEN,
        x_optional_boolean: bool | NotGiven = NOT_GIVEN,
        x_optional_integer: int | NotGiven = NOT_GIVEN,
        x_optional_number: float | NotGiven = NOT_GIVEN,
        x_optional_string: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with all supported header param types.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {
            **strip_not_given(
                {
                    "X-Required-Boolean": ("true" if x_required_boolean else "false"),
                    "X-Required-Integer": str(x_required_integer),
                    "X-Required-Number": str(x_required_number),
                    "X-Required-String": x_required_string,
                    "X-Optional-Boolean": ("true" if x_optional_boolean else "false")
                    if is_given(x_optional_boolean)
                    else NOT_GIVEN,
                    "X-Optional-Integer": str(x_optional_integer) if is_given(x_optional_integer) else NOT_GIVEN,
                    "X-Optional-Number": str(x_optional_number) if is_given(x_optional_number) else NOT_GIVEN,
                    "X-Optional-String": x_optional_string,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/header_params/all_types",
            body=maybe_transform(
                {"body_argument": body_argument}, header_param_all_types_params.HeaderParamAllTypesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def client_argument(
        self,
        *,
        foo: str | NotGiven = NOT_GIVEN,
        x_custom_endpoint_header: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        The `X-Client-Secret` header shouldn't be included in params definitions as it
        is already sent as a client argument.

        Whereas the `X-Custom-Endpoint-Header` should be included as it is only used
        here.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {
            **strip_not_given({"X-Custom-Endpoint-Header": x_custom_endpoint_header}),
            **(extra_headers or {}),
        }
        return self._post(
            "/header_params/client_argument",
            body=maybe_transform({"foo": foo}, header_param_client_argument_params.HeaderParamClientArgumentParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )


class AsyncHeaderParamsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHeaderParamsResourceWithRawResponse:
        return AsyncHeaderParamsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHeaderParamsResourceWithStreamingResponse:
        return AsyncHeaderParamsResourceWithStreamingResponse(self)

    async def all_types(
        self,
        *,
        x_required_boolean: bool,
        x_required_integer: int,
        x_required_number: float,
        x_required_string: str,
        body_argument: str | NotGiven = NOT_GIVEN,
        x_optional_boolean: bool | NotGiven = NOT_GIVEN,
        x_optional_integer: int | NotGiven = NOT_GIVEN,
        x_optional_number: float | NotGiven = NOT_GIVEN,
        x_optional_string: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with all supported header param types.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {
            **strip_not_given(
                {
                    "X-Required-Boolean": ("true" if x_required_boolean else "false"),
                    "X-Required-Integer": str(x_required_integer),
                    "X-Required-Number": str(x_required_number),
                    "X-Required-String": x_required_string,
                    "X-Optional-Boolean": ("true" if x_optional_boolean else "false")
                    if is_given(x_optional_boolean)
                    else NOT_GIVEN,
                    "X-Optional-Integer": str(x_optional_integer) if is_given(x_optional_integer) else NOT_GIVEN,
                    "X-Optional-Number": str(x_optional_number) if is_given(x_optional_number) else NOT_GIVEN,
                    "X-Optional-String": x_optional_string,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/header_params/all_types",
            body=await async_maybe_transform(
                {"body_argument": body_argument}, header_param_all_types_params.HeaderParamAllTypesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def client_argument(
        self,
        *,
        foo: str | NotGiven = NOT_GIVEN,
        x_custom_endpoint_header: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        The `X-Client-Secret` header shouldn't be included in params definitions as it
        is already sent as a client argument.

        Whereas the `X-Custom-Endpoint-Header` should be included as it is only used
        here.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {
            **strip_not_given({"X-Custom-Endpoint-Header": x_custom_endpoint_header}),
            **(extra_headers or {}),
        }
        return await self._post(
            "/header_params/client_argument",
            body=await async_maybe_transform(
                {"foo": foo}, header_param_client_argument_params.HeaderParamClientArgumentParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )


class HeaderParamsResourceWithRawResponse:
    def __init__(self, header_params: HeaderParamsResource) -> None:
        self._header_params = header_params

        self.all_types = to_raw_response_wrapper(
            header_params.all_types,
        )
        self.client_argument = to_raw_response_wrapper(
            header_params.client_argument,
        )


class AsyncHeaderParamsResourceWithRawResponse:
    def __init__(self, header_params: AsyncHeaderParamsResource) -> None:
        self._header_params = header_params

        self.all_types = async_to_raw_response_wrapper(
            header_params.all_types,
        )
        self.client_argument = async_to_raw_response_wrapper(
            header_params.client_argument,
        )


class HeaderParamsResourceWithStreamingResponse:
    def __init__(self, header_params: HeaderParamsResource) -> None:
        self._header_params = header_params

        self.all_types = to_streamed_response_wrapper(
            header_params.all_types,
        )
        self.client_argument = to_streamed_response_wrapper(
            header_params.client_argument,
        )


class AsyncHeaderParamsResourceWithStreamingResponse:
    def __init__(self, header_params: AsyncHeaderParamsResource) -> None:
        self._header_params = header_params

        self.all_types = async_to_streamed_response_wrapper(
            header_params.all_types,
        )
        self.client_argument = async_to_streamed_response_wrapper(
            header_params.client_argument,
        )
