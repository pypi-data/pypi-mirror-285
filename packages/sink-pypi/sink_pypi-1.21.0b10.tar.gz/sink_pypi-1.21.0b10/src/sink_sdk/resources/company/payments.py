# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.company.company_payment import CompanyPayment

__all__ = ["PaymentsResource", "AsyncPaymentsResource"]


class PaymentsResource(SyncAPIResource):
    """For paying Stainless $$$"""

    @cached_property
    def with_raw_response(self) -> PaymentsResourceWithRawResponse:
        return PaymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PaymentsResourceWithStreamingResponse:
        return PaymentsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        payment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompanyPayment:
        """
        Get a payment that the company made.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not payment_id:
            raise ValueError(f"Expected a non-empty value for `payment_id` but received {payment_id!r}")
        return self._get(
            f"/company/payments/{payment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompanyPayment,
        )


class AsyncPaymentsResource(AsyncAPIResource):
    """For paying Stainless $$$"""

    @cached_property
    def with_raw_response(self) -> AsyncPaymentsResourceWithRawResponse:
        return AsyncPaymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPaymentsResourceWithStreamingResponse:
        return AsyncPaymentsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        payment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompanyPayment:
        """
        Get a payment that the company made.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not payment_id:
            raise ValueError(f"Expected a non-empty value for `payment_id` but received {payment_id!r}")
        return await self._get(
            f"/company/payments/{payment_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompanyPayment,
        )


class PaymentsResourceWithRawResponse:
    def __init__(self, payments: PaymentsResource) -> None:
        self._payments = payments

        self.retrieve = to_raw_response_wrapper(
            payments.retrieve,
        )


class AsyncPaymentsResourceWithRawResponse:
    def __init__(self, payments: AsyncPaymentsResource) -> None:
        self._payments = payments

        self.retrieve = async_to_raw_response_wrapper(
            payments.retrieve,
        )


class PaymentsResourceWithStreamingResponse:
    def __init__(self, payments: PaymentsResource) -> None:
        self._payments = payments

        self.retrieve = to_streamed_response_wrapper(
            payments.retrieve,
        )


class AsyncPaymentsResourceWithStreamingResponse:
    def __init__(self, payments: AsyncPaymentsResource) -> None:
        self._payments = payments

        self.retrieve = async_to_streamed_response_wrapper(
            payments.retrieve,
        )
