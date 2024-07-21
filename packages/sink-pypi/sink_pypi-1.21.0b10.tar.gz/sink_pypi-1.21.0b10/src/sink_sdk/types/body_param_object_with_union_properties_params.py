# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

from ..types import shared_params
from .my_model_param import MyModelParam

__all__ = ["BodyParamObjectWithUnionPropertiesParams", "Bar", "BarObjectWithModelProperty"]


class BodyParamObjectWithUnionPropertiesParams(TypedDict, total=False):
    bar: Required[Bar]

    foo: Required[Union[float, str, bool, object]]


class BarObjectWithModelProperty(TypedDict, total=False):
    foo: str

    my_model: MyModelParam


Bar = Union[shared_params.SimpleObject, BarObjectWithModelProperty]
