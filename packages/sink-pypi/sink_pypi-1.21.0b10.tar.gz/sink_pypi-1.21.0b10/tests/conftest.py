from __future__ import annotations

import os
import asyncio
import logging
from typing import TYPE_CHECKING, Iterator, AsyncIterator

import pytest

from sink_sdk import Sink, AsyncSink

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("sink_sdk").setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

user_token = "My User Token"
username = "Robert"
some_number_arg_required_no_default = 0
some_number_arg_required_no_default_no_env = 0
required_arg_no_env = "<example>"


@pytest.fixture(scope="session")
def client(request: FixtureRequest) -> Iterator[Sink]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    with Sink(
        base_url=base_url,
        user_token=user_token,
        username=username,
        some_number_arg_required_no_default=some_number_arg_required_no_default,
        some_number_arg_required_no_default_no_env=some_number_arg_required_no_default_no_env,
        required_arg_no_env=required_arg_no_env,
        _strict_response_validation=strict,
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def async_client(request: FixtureRequest) -> AsyncIterator[AsyncSink]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    async with AsyncSink(
        base_url=base_url,
        user_token=user_token,
        username=username,
        some_number_arg_required_no_default=some_number_arg_required_no_default,
        some_number_arg_required_no_default_no_env=some_number_arg_required_no_default_no_env,
        required_arg_no_env=required_arg_no_env,
        _strict_response_validation=strict,
    ) as client:
        yield client
