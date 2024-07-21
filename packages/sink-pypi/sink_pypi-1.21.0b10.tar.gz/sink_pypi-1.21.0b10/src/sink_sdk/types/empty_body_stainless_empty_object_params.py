# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EmptyBodyStainlessEmptyObjectParams", "Body"]


class EmptyBodyStainlessEmptyObjectParams(TypedDict, total=False):
    body: Required[Body]

    query_param: str
    """Query param description"""

    second_query_param: str
    """Query param description"""


class Body(TypedDict, total=False):
    pass
