# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.names import param_options_param_params, param_timeout_param_params
from ..._base_client import make_request_options

__all__ = ["ParamsResource", "AsyncParamsResource"]


class ParamsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ParamsResourceWithRawResponse:
        return ParamsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ParamsResourceWithStreamingResponse:
        return ParamsResourceWithStreamingResponse(self)

    def options_param(
        self,
        *,
        options: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a `requestBody` that has a property named `options`

        Args:
          options: my options request parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/names/body_params/options",
            body=maybe_transform({"options": options}, param_options_param_params.ParamOptionsParamParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def timeout_param(
        self,
        *,
        url_timeout: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a `requestBody` that has a property named `timeout`

        Args:
          url_timeout: my timeout request parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/names/body_params/timeout",
            body=maybe_transform({"timeout": url_timeout}, param_timeout_param_params.ParamTimeoutParamParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )


class AsyncParamsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncParamsResourceWithRawResponse:
        return AsyncParamsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncParamsResourceWithStreamingResponse:
        return AsyncParamsResourceWithStreamingResponse(self)

    async def options_param(
        self,
        *,
        options: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a `requestBody` that has a property named `options`

        Args:
          options: my options request parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/names/body_params/options",
            body=await async_maybe_transform({"options": options}, param_options_param_params.ParamOptionsParamParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def timeout_param(
        self,
        *,
        url_timeout: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint with a `requestBody` that has a property named `timeout`

        Args:
          url_timeout: my timeout request parameter

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/names/body_params/timeout",
            body=await async_maybe_transform(
                {"timeout": url_timeout}, param_timeout_param_params.ParamTimeoutParamParams
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


class ParamsResourceWithRawResponse:
    def __init__(self, params: ParamsResource) -> None:
        self._params = params

        self.options_param = to_raw_response_wrapper(
            params.options_param,
        )
        self.timeout_param = to_raw_response_wrapper(
            params.timeout_param,
        )


class AsyncParamsResourceWithRawResponse:
    def __init__(self, params: AsyncParamsResource) -> None:
        self._params = params

        self.options_param = async_to_raw_response_wrapper(
            params.options_param,
        )
        self.timeout_param = async_to_raw_response_wrapper(
            params.timeout_param,
        )


class ParamsResourceWithStreamingResponse:
    def __init__(self, params: ParamsResource) -> None:
        self._params = params

        self.options_param = to_streamed_response_wrapper(
            params.options_param,
        )
        self.timeout_param = to_streamed_response_wrapper(
            params.timeout_param,
        )


class AsyncParamsResourceWithStreamingResponse:
    def __init__(self, params: AsyncParamsResource) -> None:
        self._params = params

        self.options_param = async_to_streamed_response_wrapper(
            params.options_param,
        )
        self.timeout_param = async_to_streamed_response_wrapper(
            params.timeout_param,
        )
