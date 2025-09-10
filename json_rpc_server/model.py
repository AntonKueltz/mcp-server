from __future__ import annotations
from typing import TypeAlias
from typing_extensions import TypeAliasType

from pydantic import BaseModel

NumberType: TypeAlias = int | float
PrimitiveType: TypeAlias = str | NumberType | bool | None
StructuredType = TypeAliasType(
    "StructuredType",
    dict[str, "StructuredType | PrimitiveType"]
    | list["StructuredType | PrimitiveType"],
)
JsonType: TypeAlias = StructuredType | PrimitiveType

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: StructuredType | None
    id: str | NumberType | None


class JsonRpcResponse(BaseModel):
    jsonrpc: str
    id: str | NumberType | None


class JsonRpcSuccessResponse(JsonRpcResponse):
    result: JsonType


class JsonRpcErrorObject(BaseModel):
    code: int
    message: str
    data: JsonType


class JsonRpcErrorResponse(JsonRpcResponse):
    error: JsonRpcErrorObject
