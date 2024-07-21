# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional

from ..._models import BaseModel
from ..shared.simple_object import SimpleObject

__all__ = ["UnionTypeNullableUnionResponse", "BasicObject"]


class BasicObject(BaseModel):
    item: Optional[str] = None


UnionTypeNullableUnionResponse = Union[SimpleObject, BasicObject, None]
