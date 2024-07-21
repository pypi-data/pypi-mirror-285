# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional

from ..._models import BaseModel
from ..shared.simple_object import SimpleObject

__all__ = ["UnionTypeSuperMixedTypesResponse", "BasicObject"]


class BasicObject(BaseModel):
    item: Optional[str] = None


UnionTypeSuperMixedTypesResponse = Union[SimpleObject, BasicObject, bool, str, object, object]
