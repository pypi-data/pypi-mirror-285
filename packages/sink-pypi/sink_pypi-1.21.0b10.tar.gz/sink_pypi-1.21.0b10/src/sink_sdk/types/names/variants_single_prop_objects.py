# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional

from ..._models import BaseModel

__all__ = ["VariantsSinglePropObjects", "Foo", "Bar"]


class Foo(BaseModel):
    foo: Optional[str] = None


class Bar(BaseModel):
    bar: Optional[str] = None


VariantsSinglePropObjects = Union[Foo, Bar]
