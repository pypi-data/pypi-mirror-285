# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["BodyParamTopLevelOneOfResponse", "ObjectWithRequiredEnum", "SimpleObjectWithRequiredProperty"]


class ObjectWithRequiredEnum(BaseModel):
    kind: Literal["VIRTUAL", "PHYSICAL"]


class SimpleObjectWithRequiredProperty(BaseModel):
    is_foo: bool


BodyParamTopLevelOneOfResponse = Union[ObjectWithRequiredEnum, SimpleObjectWithRequiredProperty]
