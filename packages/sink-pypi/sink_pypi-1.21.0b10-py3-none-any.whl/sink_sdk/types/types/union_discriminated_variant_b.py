# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["UnionDiscriminatedVariantB"]


class UnionDiscriminatedVariantB(BaseModel):
    type: Literal["b"]

    value_from_b: str
