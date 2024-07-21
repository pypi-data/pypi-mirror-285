# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional

from ..._models import BaseModel
from ..shared.simple_object import SimpleObject

__all__ = ["UnionTypeMixedTypesResponse", "BasicObject"]


class BasicObject(BaseModel):
    item: Optional[str] = None


UnionTypeMixedTypesResponse = Union[SimpleObject, BasicObject, bool]
