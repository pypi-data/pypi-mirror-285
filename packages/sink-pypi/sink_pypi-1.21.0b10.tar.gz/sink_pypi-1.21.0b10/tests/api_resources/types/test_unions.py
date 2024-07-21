# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sink_sdk import Sink, AsyncSink
from tests.utils import assert_matches_type
from sink_sdk.types.types import UnionDiscriminatedByPropertyNameResponse, UnionDiscriminatedWithBasicMappingResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUnions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_discriminated_by_property_name(self, client: Sink) -> None:
        union = client.types.unions.discriminated_by_property_name()
        assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

    @parametrize
    def test_raw_response_discriminated_by_property_name(self, client: Sink) -> None:
        response = client.types.unions.with_raw_response.discriminated_by_property_name()

        assert response.is_closed is True
        union = response.parse()
        assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

    @parametrize
    def test_streaming_response_discriminated_by_property_name(self, client: Sink) -> None:
        with client.types.unions.with_streaming_response.discriminated_by_property_name() as response:
            assert not response.is_closed

            union = response.parse()
            assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_discriminated_with_basic_mapping(self, client: Sink) -> None:
        union = client.types.unions.discriminated_with_basic_mapping()
        assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

    @parametrize
    def test_raw_response_discriminated_with_basic_mapping(self, client: Sink) -> None:
        response = client.types.unions.with_raw_response.discriminated_with_basic_mapping()

        assert response.is_closed is True
        union = response.parse()
        assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

    @parametrize
    def test_streaming_response_discriminated_with_basic_mapping(self, client: Sink) -> None:
        with client.types.unions.with_streaming_response.discriminated_with_basic_mapping() as response:
            assert not response.is_closed

            union = response.parse()
            assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUnions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_discriminated_by_property_name(self, async_client: AsyncSink) -> None:
        union = await async_client.types.unions.discriminated_by_property_name()
        assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

    @parametrize
    async def test_raw_response_discriminated_by_property_name(self, async_client: AsyncSink) -> None:
        response = await async_client.types.unions.with_raw_response.discriminated_by_property_name()

        assert response.is_closed is True
        union = await response.parse()
        assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

    @parametrize
    async def test_streaming_response_discriminated_by_property_name(self, async_client: AsyncSink) -> None:
        async with async_client.types.unions.with_streaming_response.discriminated_by_property_name() as response:
            assert not response.is_closed

            union = await response.parse()
            assert_matches_type(UnionDiscriminatedByPropertyNameResponse, union, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_discriminated_with_basic_mapping(self, async_client: AsyncSink) -> None:
        union = await async_client.types.unions.discriminated_with_basic_mapping()
        assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

    @parametrize
    async def test_raw_response_discriminated_with_basic_mapping(self, async_client: AsyncSink) -> None:
        response = await async_client.types.unions.with_raw_response.discriminated_with_basic_mapping()

        assert response.is_closed is True
        union = await response.parse()
        assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

    @parametrize
    async def test_streaming_response_discriminated_with_basic_mapping(self, async_client: AsyncSink) -> None:
        async with async_client.types.unions.with_streaming_response.discriminated_with_basic_mapping() as response:
            assert not response.is_closed

            union = await response.parse()
            assert_matches_type(UnionDiscriminatedWithBasicMappingResponse, union, path=["response"])

        assert cast(Any, response.is_closed) is True
