# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

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
from ...types.types import (
    enum_basic_params,
    enum_array_unique_values_params,
    enum_array_unique_values_numbers_params,
    enum_array_unique_values_2_values_params,
)
from ..._base_client import make_request_options
from ...types.shared.currency import Currency
from ...types.types.enum_basic_response import EnumBasicResponse

__all__ = ["EnumsResource", "AsyncEnumsResource"]


class EnumsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EnumsResourceWithRawResponse:
        return EnumsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EnumsResourceWithStreamingResponse:
        return EnumsResourceWithStreamingResponse(self)

    def array_unique_values(
        self,
        *,
        body: List[Literal["USD", "GBP", "PAB", "AED"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values",
            body=maybe_transform(body, enum_array_unique_values_params.EnumArrayUniqueValuesParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def array_unique_values_2_values(
        self,
        *,
        body: List[Literal["USD", "GBP"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values_2_values",
            body=maybe_transform(body, enum_array_unique_values_2_values_params.EnumArrayUniqueValues2ValuesParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def array_unique_values_numbers(
        self,
        *,
        body: Iterable[Literal[5, 6, 7, 8, 9]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/types/enum_tests_array_unique_values_numbers",
            body=maybe_transform(body, enum_array_unique_values_numbers_params.EnumArrayUniqueValuesNumbersParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def basic(
        self,
        *,
        input_currency: Currency | NotGiven = NOT_GIVEN,
        problematic_enum: Literal["123_FOO", "30%", "*", ""] | NotGiven = NOT_GIVEN,
        uses_const: Literal["my_const_enum_value"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> EnumBasicResponse:
        """
        Endpoint that has a `$ref`d enum type in the request body and the response body.

        Args:
          input_currency: This is my description for the Currency enum

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/types/enums",
            body=maybe_transform(
                {
                    "input_currency": input_currency,
                    "problematic_enum": problematic_enum,
                    "uses_const": uses_const,
                },
                enum_basic_params.EnumBasicParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=EnumBasicResponse,
        )


class AsyncEnumsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEnumsResourceWithRawResponse:
        return AsyncEnumsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEnumsResourceWithStreamingResponse:
        return AsyncEnumsResourceWithStreamingResponse(self)

    async def array_unique_values(
        self,
        *,
        body: List[Literal["USD", "GBP", "PAB", "AED"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values",
            body=await async_maybe_transform(body, enum_array_unique_values_params.EnumArrayUniqueValuesParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def array_unique_values_2_values(
        self,
        *,
        body: List[Literal["USD", "GBP"]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values_2_values",
            body=await async_maybe_transform(
                body, enum_array_unique_values_2_values_params.EnumArrayUniqueValues2ValuesParams
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

    async def array_unique_values_numbers(
        self,
        *,
        body: Iterable[Literal[5, 6, 7, 8, 9]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Endpoint that has an array of enum that should generate a valid test with 2
        non-repeating values in the array.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/types/enum_tests_array_unique_values_numbers",
            body=await async_maybe_transform(
                body, enum_array_unique_values_numbers_params.EnumArrayUniqueValuesNumbersParams
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

    async def basic(
        self,
        *,
        input_currency: Currency | NotGiven = NOT_GIVEN,
        problematic_enum: Literal["123_FOO", "30%", "*", ""] | NotGiven = NOT_GIVEN,
        uses_const: Literal["my_const_enum_value"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> EnumBasicResponse:
        """
        Endpoint that has a `$ref`d enum type in the request body and the response body.

        Args:
          input_currency: This is my description for the Currency enum

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/types/enums",
            body=await async_maybe_transform(
                {
                    "input_currency": input_currency,
                    "problematic_enum": problematic_enum,
                    "uses_const": uses_const,
                },
                enum_basic_params.EnumBasicParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=EnumBasicResponse,
        )


class EnumsResourceWithRawResponse:
    def __init__(self, enums: EnumsResource) -> None:
        self._enums = enums

        self.array_unique_values = to_raw_response_wrapper(
            enums.array_unique_values,
        )
        self.array_unique_values_2_values = to_raw_response_wrapper(
            enums.array_unique_values_2_values,
        )
        self.array_unique_values_numbers = to_raw_response_wrapper(
            enums.array_unique_values_numbers,
        )
        self.basic = to_raw_response_wrapper(
            enums.basic,
        )


class AsyncEnumsResourceWithRawResponse:
    def __init__(self, enums: AsyncEnumsResource) -> None:
        self._enums = enums

        self.array_unique_values = async_to_raw_response_wrapper(
            enums.array_unique_values,
        )
        self.array_unique_values_2_values = async_to_raw_response_wrapper(
            enums.array_unique_values_2_values,
        )
        self.array_unique_values_numbers = async_to_raw_response_wrapper(
            enums.array_unique_values_numbers,
        )
        self.basic = async_to_raw_response_wrapper(
            enums.basic,
        )


class EnumsResourceWithStreamingResponse:
    def __init__(self, enums: EnumsResource) -> None:
        self._enums = enums

        self.array_unique_values = to_streamed_response_wrapper(
            enums.array_unique_values,
        )
        self.array_unique_values_2_values = to_streamed_response_wrapper(
            enums.array_unique_values_2_values,
        )
        self.array_unique_values_numbers = to_streamed_response_wrapper(
            enums.array_unique_values_numbers,
        )
        self.basic = to_streamed_response_wrapper(
            enums.basic,
        )


class AsyncEnumsResourceWithStreamingResponse:
    def __init__(self, enums: AsyncEnumsResource) -> None:
        self._enums = enums

        self.array_unique_values = async_to_streamed_response_wrapper(
            enums.array_unique_values,
        )
        self.array_unique_values_2_values = async_to_streamed_response_wrapper(
            enums.array_unique_values_2_values,
        )
        self.array_unique_values_numbers = async_to_streamed_response_wrapper(
            enums.array_unique_values_numbers,
        )
        self.basic = async_to_streamed_response_wrapper(
            enums.basic,
        )
