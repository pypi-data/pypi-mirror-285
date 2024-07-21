# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.model_from_schemas_ref import ModelFromSchemasRef
from ..types.config_tool_model_ref_from_nested_response_body_response import (
    ConfigToolModelRefFromNestedResponseBodyResponse,
)

__all__ = ["ConfigToolsResource", "AsyncConfigToolsResource"]


class ConfigToolsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigToolsResourceWithRawResponse:
        return ConfigToolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigToolsResourceWithStreamingResponse:
        return ConfigToolsResourceWithStreamingResponse(self)

    def model_ref_from_nested_response_body(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigToolModelRefFromNestedResponseBodyResponse:
        return self._get(
            "/config_tools/model_refs/from_nested_response",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigToolModelRefFromNestedResponseBodyResponse,
        )

    def model_ref_from_schemas(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelFromSchemasRef:
        return self._get(
            "/config_tools/model_refs/from_schemas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelFromSchemasRef,
        )


class AsyncConfigToolsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigToolsResourceWithRawResponse:
        return AsyncConfigToolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigToolsResourceWithStreamingResponse:
        return AsyncConfigToolsResourceWithStreamingResponse(self)

    async def model_ref_from_nested_response_body(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConfigToolModelRefFromNestedResponseBodyResponse:
        return await self._get(
            "/config_tools/model_refs/from_nested_response",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConfigToolModelRefFromNestedResponseBodyResponse,
        )

    async def model_ref_from_schemas(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelFromSchemasRef:
        return await self._get(
            "/config_tools/model_refs/from_schemas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelFromSchemasRef,
        )


class ConfigToolsResourceWithRawResponse:
    def __init__(self, config_tools: ConfigToolsResource) -> None:
        self._config_tools = config_tools

        self.model_ref_from_nested_response_body = to_raw_response_wrapper(
            config_tools.model_ref_from_nested_response_body,
        )
        self.model_ref_from_schemas = to_raw_response_wrapper(
            config_tools.model_ref_from_schemas,
        )


class AsyncConfigToolsResourceWithRawResponse:
    def __init__(self, config_tools: AsyncConfigToolsResource) -> None:
        self._config_tools = config_tools

        self.model_ref_from_nested_response_body = async_to_raw_response_wrapper(
            config_tools.model_ref_from_nested_response_body,
        )
        self.model_ref_from_schemas = async_to_raw_response_wrapper(
            config_tools.model_ref_from_schemas,
        )


class ConfigToolsResourceWithStreamingResponse:
    def __init__(self, config_tools: ConfigToolsResource) -> None:
        self._config_tools = config_tools

        self.model_ref_from_nested_response_body = to_streamed_response_wrapper(
            config_tools.model_ref_from_nested_response_body,
        )
        self.model_ref_from_schemas = to_streamed_response_wrapper(
            config_tools.model_ref_from_schemas,
        )


class AsyncConfigToolsResourceWithStreamingResponse:
    def __init__(self, config_tools: AsyncConfigToolsResource) -> None:
        self._config_tools = config_tools

        self.model_ref_from_nested_response_body = async_to_streamed_response_wrapper(
            config_tools.model_ref_from_nested_response_body,
        )
        self.model_ref_from_schemas = async_to_streamed_response_wrapper(
            config_tools.model_ref_from_schemas,
        )
