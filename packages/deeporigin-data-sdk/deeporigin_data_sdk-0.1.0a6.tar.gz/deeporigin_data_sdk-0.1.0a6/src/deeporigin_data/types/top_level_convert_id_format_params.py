# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["TopLevelConvertIDFormatParams", "Conversion", "ConversionID", "ConversionHid"]


class TopLevelConvertIDFormatParams(TypedDict, total=False):
    conversions: Required[Iterable[Conversion]]


class ConversionID(TypedDict, total=False):
    id: Required[str]
    """Deep Origin system ID."""


class ConversionHid(TypedDict, total=False):
    hid: Required[str]


Conversion = Union[ConversionID, ConversionHid]
