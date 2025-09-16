from __future__ import annotations
from typing import TypeAlias
from typing_extensions import TypeAliasType

NumberType: TypeAlias = int | float
PrimitiveType: TypeAlias = str | NumberType | bool | None
StructuredType = TypeAliasType(
    "StructuredType",
    dict[str, "StructuredType | PrimitiveType"]
    | list["StructuredType | PrimitiveType"],
)
JsonType: TypeAlias = StructuredType | PrimitiveType
MethodResult: TypeAlias = tuple[JsonType, dict[str, str]]  # (result, headers)
