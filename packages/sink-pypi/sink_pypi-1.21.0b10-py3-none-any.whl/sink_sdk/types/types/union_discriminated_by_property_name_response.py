# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated

from ..._utils import PropertyInfo
from .union_discriminated_variant_a import UnionDiscriminatedVariantA
from .union_discriminated_variant_b import UnionDiscriminatedVariantB

__all__ = ["UnionDiscriminatedByPropertyNameResponse"]

UnionDiscriminatedByPropertyNameResponse = Annotated[
    Union[UnionDiscriminatedVariantA, UnionDiscriminatedVariantB], PropertyInfo(discriminator="type")
]
