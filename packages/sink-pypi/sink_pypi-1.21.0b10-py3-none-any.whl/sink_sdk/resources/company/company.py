# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .payments import (
    PaymentsResource,
    AsyncPaymentsResource,
    PaymentsResourceWithRawResponse,
    AsyncPaymentsResourceWithRawResponse,
    PaymentsResourceWithStreamingResponse,
    AsyncPaymentsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["CompanyResource", "AsyncCompanyResource"]


class CompanyResource(SyncAPIResource):
    """Stainless API company"""

    @cached_property
    def payments(self) -> PaymentsResource:
        """For paying Stainless $$$"""
        return PaymentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CompanyResourceWithRawResponse:
        return CompanyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompanyResourceWithStreamingResponse:
        return CompanyResourceWithStreamingResponse(self)


class AsyncCompanyResource(AsyncAPIResource):
    """Stainless API company"""

    @cached_property
    def payments(self) -> AsyncPaymentsResource:
        """For paying Stainless $$$"""
        return AsyncPaymentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCompanyResourceWithRawResponse:
        return AsyncCompanyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompanyResourceWithStreamingResponse:
        return AsyncCompanyResourceWithStreamingResponse(self)


class CompanyResourceWithRawResponse:
    def __init__(self, company: CompanyResource) -> None:
        self._company = company

    @cached_property
    def payments(self) -> PaymentsResourceWithRawResponse:
        """For paying Stainless $$$"""
        return PaymentsResourceWithRawResponse(self._company.payments)


class AsyncCompanyResourceWithRawResponse:
    def __init__(self, company: AsyncCompanyResource) -> None:
        self._company = company

    @cached_property
    def payments(self) -> AsyncPaymentsResourceWithRawResponse:
        """For paying Stainless $$$"""
        return AsyncPaymentsResourceWithRawResponse(self._company.payments)


class CompanyResourceWithStreamingResponse:
    def __init__(self, company: CompanyResource) -> None:
        self._company = company

    @cached_property
    def payments(self) -> PaymentsResourceWithStreamingResponse:
        """For paying Stainless $$$"""
        return PaymentsResourceWithStreamingResponse(self._company.payments)


class AsyncCompanyResourceWithStreamingResponse:
    def __init__(self, company: AsyncCompanyResource) -> None:
        self._company = company

    @cached_property
    def payments(self) -> AsyncPaymentsResourceWithStreamingResponse:
        """For paying Stainless $$$"""
        return AsyncPaymentsResourceWithStreamingResponse(self._company.payments)
