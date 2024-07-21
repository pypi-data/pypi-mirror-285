# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import (
    SyncPagePageNumber,
    AsyncPagePageNumber,
    SyncPagePageNumberWithoutCurrentPageResponse,
    AsyncPagePageNumberWithoutCurrentPageResponse,
)
from ..._base_client import AsyncPaginator, make_request_options
from ...types.my_model import MyModel
from ...types.pagination_tests import page_number_list_params, page_number_list_without_current_page_response_params

__all__ = ["PageNumberResource", "AsyncPageNumberResource"]


class PageNumberResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PageNumberResourceWithRawResponse:
        return PageNumberResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PageNumberResourceWithStreamingResponse:
        return PageNumberResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPagePageNumber[MyModel]:
        """
        Test case for page_number pagination

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/page_number",
            page=SyncPagePageNumber[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    page_number_list_params.PageNumberListParams,
                ),
            ),
            model=MyModel,
        )

    def list_without_current_page_response(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        prop_to_not_mess_with_infer_for_other_pages: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPagePageNumberWithoutCurrentPageResponse[MyModel]:
        """
        Test case for page_number pagination without a `page` response property

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/page_number_without_current_page_response",
            page=SyncPagePageNumberWithoutCurrentPageResponse[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "prop_to_not_mess_with_infer_for_other_pages": prop_to_not_mess_with_infer_for_other_pages,
                    },
                    page_number_list_without_current_page_response_params.PageNumberListWithoutCurrentPageResponseParams,
                ),
            ),
            model=MyModel,
        )


class AsyncPageNumberResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPageNumberResourceWithRawResponse:
        return AsyncPageNumberResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPageNumberResourceWithStreamingResponse:
        return AsyncPageNumberResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[MyModel, AsyncPagePageNumber[MyModel]]:
        """
        Test case for page_number pagination

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/page_number",
            page=AsyncPagePageNumber[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    page_number_list_params.PageNumberListParams,
                ),
            ),
            model=MyModel,
        )

    def list_without_current_page_response(
        self,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        prop_to_not_mess_with_infer_for_other_pages: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[MyModel, AsyncPagePageNumberWithoutCurrentPageResponse[MyModel]]:
        """
        Test case for page_number pagination without a `page` response property

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/paginated/page_number_without_current_page_response",
            page=AsyncPagePageNumberWithoutCurrentPageResponse[MyModel],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                        "prop_to_not_mess_with_infer_for_other_pages": prop_to_not_mess_with_infer_for_other_pages,
                    },
                    page_number_list_without_current_page_response_params.PageNumberListWithoutCurrentPageResponseParams,
                ),
            ),
            model=MyModel,
        )


class PageNumberResourceWithRawResponse:
    def __init__(self, page_number: PageNumberResource) -> None:
        self._page_number = page_number

        self.list = to_raw_response_wrapper(
            page_number.list,
        )
        self.list_without_current_page_response = to_raw_response_wrapper(
            page_number.list_without_current_page_response,
        )


class AsyncPageNumberResourceWithRawResponse:
    def __init__(self, page_number: AsyncPageNumberResource) -> None:
        self._page_number = page_number

        self.list = async_to_raw_response_wrapper(
            page_number.list,
        )
        self.list_without_current_page_response = async_to_raw_response_wrapper(
            page_number.list_without_current_page_response,
        )


class PageNumberResourceWithStreamingResponse:
    def __init__(self, page_number: PageNumberResource) -> None:
        self._page_number = page_number

        self.list = to_streamed_response_wrapper(
            page_number.list,
        )
        self.list_without_current_page_response = to_streamed_response_wrapper(
            page_number.list_without_current_page_response,
        )


class AsyncPageNumberResourceWithStreamingResponse:
    def __init__(self, page_number: AsyncPageNumberResource) -> None:
        self._page_number = page_number

        self.list = async_to_streamed_response_wrapper(
            page_number.list,
        )
        self.list_without_current_page_response = async_to_streamed_response_wrapper(
            page_number.list_without_current_page_response,
        )
