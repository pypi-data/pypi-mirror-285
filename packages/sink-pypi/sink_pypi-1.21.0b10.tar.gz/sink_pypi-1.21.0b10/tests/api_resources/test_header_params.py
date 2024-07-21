# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sink_sdk import Sink, AsyncSink

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHeaderParams:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_all_types(self, client: Sink) -> None:
        header_param = client.header_params.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        )
        assert header_param is None

    @parametrize
    def test_method_all_types_with_all_params(self, client: Sink) -> None:
        header_param = client.header_params.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
            body_argument="body_argument",
            x_optional_boolean=True,
            x_optional_integer=0,
            x_optional_number=0,
            x_optional_string="X-Optional-String",
        )
        assert header_param is None

    @parametrize
    def test_raw_response_all_types(self, client: Sink) -> None:
        response = client.header_params.with_raw_response.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        )

        assert response.is_closed is True
        header_param = response.parse()
        assert header_param is None

    @parametrize
    def test_streaming_response_all_types(self, client: Sink) -> None:
        with client.header_params.with_streaming_response.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        ) as response:
            assert not response.is_closed

            header_param = response.parse()
            assert header_param is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_client_argument(self, client: Sink) -> None:
        header_param = client.header_params.client_argument()
        assert header_param is None

    @parametrize
    def test_method_client_argument_with_all_params(self, client: Sink) -> None:
        header_param = client.header_params.client_argument(
            foo="foo",
            x_custom_endpoint_header="X-Custom-Endpoint-Header",
        )
        assert header_param is None

    @parametrize
    def test_raw_response_client_argument(self, client: Sink) -> None:
        response = client.header_params.with_raw_response.client_argument()

        assert response.is_closed is True
        header_param = response.parse()
        assert header_param is None

    @parametrize
    def test_streaming_response_client_argument(self, client: Sink) -> None:
        with client.header_params.with_streaming_response.client_argument() as response:
            assert not response.is_closed

            header_param = response.parse()
            assert header_param is None

        assert cast(Any, response.is_closed) is True


class TestAsyncHeaderParams:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_all_types(self, async_client: AsyncSink) -> None:
        header_param = await async_client.header_params.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        )
        assert header_param is None

    @parametrize
    async def test_method_all_types_with_all_params(self, async_client: AsyncSink) -> None:
        header_param = await async_client.header_params.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
            body_argument="body_argument",
            x_optional_boolean=True,
            x_optional_integer=0,
            x_optional_number=0,
            x_optional_string="X-Optional-String",
        )
        assert header_param is None

    @parametrize
    async def test_raw_response_all_types(self, async_client: AsyncSink) -> None:
        response = await async_client.header_params.with_raw_response.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        )

        assert response.is_closed is True
        header_param = await response.parse()
        assert header_param is None

    @parametrize
    async def test_streaming_response_all_types(self, async_client: AsyncSink) -> None:
        async with async_client.header_params.with_streaming_response.all_types(
            x_required_boolean=True,
            x_required_integer=0,
            x_required_number=0,
            x_required_string="X-Required-String",
        ) as response:
            assert not response.is_closed

            header_param = await response.parse()
            assert header_param is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_client_argument(self, async_client: AsyncSink) -> None:
        header_param = await async_client.header_params.client_argument()
        assert header_param is None

    @parametrize
    async def test_method_client_argument_with_all_params(self, async_client: AsyncSink) -> None:
        header_param = await async_client.header_params.client_argument(
            foo="foo",
            x_custom_endpoint_header="X-Custom-Endpoint-Header",
        )
        assert header_param is None

    @parametrize
    async def test_raw_response_client_argument(self, async_client: AsyncSink) -> None:
        response = await async_client.header_params.with_raw_response.client_argument()

        assert response.is_closed is True
        header_param = await response.parse()
        assert header_param is None

    @parametrize
    async def test_streaming_response_client_argument(self, async_client: AsyncSink) -> None:
        async with async_client.header_params.with_streaming_response.client_argument() as response:
            assert not response.is_closed

            header_param = await response.parse()
            assert header_param is None

        assert cast(Any, response.is_closed) is True
