# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json

import httpx

from .._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["OnlyCustomMethodsResource", "AsyncOnlyCustomMethodsResource"]


class OnlyCustomMethodsResource(SyncAPIResource):
    def get_auth_url(
        self,
        *,
        print_data: bool,
        redirect_uri: str,
        client_id: str,
    ) -> str:
        """A top level custom method on the sink customer."""
        if print_data:
            # used to test imports
            print(json.dumps("foo"))  # noqa: T201

        return str(
            httpx.URL(
                "http://localhost:8000/auth",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                },
            )
        )


class AsyncOnlyCustomMethodsResource(AsyncAPIResource):
    def get_auth_url(
        self,
        *,
        print_data: bool,
        redirect_uri: str,
        client_id: str,
    ) -> str:
        """A top level custom method on the sink customer."""
        if print_data:
            # used to test imports
            print(json.dumps("foo"))  # noqa: T201

        return str(
            httpx.URL(
                "http://localhost:8000/auth",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                },
            )
        )
