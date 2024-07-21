# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sink_sdk import Sink, AsyncSink
from tests.utils import assert_matches_type
from sink_sdk.types import APIStatus

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTopLevel:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_api_status(self, client: Sink) -> None:
        top_level = client.api_status()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    def test_raw_response_api_status(self, client: Sink) -> None:
        response = client.with_raw_response.api_status()

        assert response.is_closed is True
        top_level = response.parse()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    def test_streaming_response_api_status(self, client: Sink) -> None:
        with client.with_streaming_response.api_status() as response:
            assert not response.is_closed

            top_level = response.parse()
            assert_matches_type(APIStatus, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_api_status_alias(self, client: Sink) -> None:
        top_level = client.api_status_alias()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    def test_raw_response_api_status_alias(self, client: Sink) -> None:
        response = client.with_raw_response.api_status_alias()

        assert response.is_closed is True
        top_level = response.parse()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    def test_streaming_response_api_status_alias(self, client: Sink) -> None:
        with client.with_streaming_response.api_status_alias() as response:
            assert not response.is_closed

            top_level = response.parse()
            assert_matches_type(APIStatus, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_no_response(self, client: Sink) -> None:
        top_level = client.create_no_response()
        assert top_level is None

    @parametrize
    def test_raw_response_create_no_response(self, client: Sink) -> None:
        response = client.with_raw_response.create_no_response()

        assert response.is_closed is True
        top_level = response.parse()
        assert top_level is None

    @parametrize
    def test_streaming_response_create_no_response(self, client: Sink) -> None:
        with client.with_streaming_response.create_no_response() as response:
            assert not response.is_closed

            top_level = response.parse()
            assert top_level is None

        assert cast(Any, response.is_closed) is True

    def test_get_auth_url(self, client: Sink) -> None:
        url = client.get_auth_url(
            print_data=False,
            redirect_uri="http://localhost:8000/auth/success",
            client_id="<client_id>",
        )
        assert (
            url
            == "http://localhost:8000/auth?client_id=%3Cclient_id%3E&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fsuccess"
        )


class TestAsyncTopLevel:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_api_status(self, async_client: AsyncSink) -> None:
        top_level = await async_client.api_status()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    async def test_raw_response_api_status(self, async_client: AsyncSink) -> None:
        response = await async_client.with_raw_response.api_status()

        assert response.is_closed is True
        top_level = await response.parse()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_api_status(self, async_client: AsyncSink) -> None:
        async with async_client.with_streaming_response.api_status() as response:
            assert not response.is_closed

            top_level = await response.parse()
            assert_matches_type(APIStatus, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_api_status_alias(self, async_client: AsyncSink) -> None:
        top_level = await async_client.api_status_alias()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    async def test_raw_response_api_status_alias(self, async_client: AsyncSink) -> None:
        response = await async_client.with_raw_response.api_status_alias()

        assert response.is_closed is True
        top_level = await response.parse()
        assert_matches_type(APIStatus, top_level, path=["response"])

    @parametrize
    async def test_streaming_response_api_status_alias(self, async_client: AsyncSink) -> None:
        async with async_client.with_streaming_response.api_status_alias() as response:
            assert not response.is_closed

            top_level = await response.parse()
            assert_matches_type(APIStatus, top_level, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_no_response(self, async_client: AsyncSink) -> None:
        top_level = await async_client.create_no_response()
        assert top_level is None

    @parametrize
    async def test_raw_response_create_no_response(self, async_client: AsyncSink) -> None:
        response = await async_client.with_raw_response.create_no_response()

        assert response.is_closed is True
        top_level = await response.parse()
        assert top_level is None

    @parametrize
    async def test_streaming_response_create_no_response(self, async_client: AsyncSink) -> None:
        async with async_client.with_streaming_response.create_no_response() as response:
            assert not response.is_closed

            top_level = await response.parse()
            assert top_level is None

        assert cast(Any, response.is_closed) is True

    def test_get_auth_url(self, client: Sink) -> None:
        url = client.get_auth_url(
            print_data=False,
            redirect_uri="http://localhost:8000/auth/success",
            client_id="<client_id>",
        )
        assert (
            url
            == "http://localhost:8000/auth?client_id=%3Cclient_id%3E&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fsuccess"
        )
