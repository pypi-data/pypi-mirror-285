# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os

import pytest

from sink_sdk import Sink

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOnlyCustomMethods:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

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


class TestAsyncOnlyCustomMethods:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

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
