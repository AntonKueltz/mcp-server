from __future__ import annotations
from typing import Annotated, TypeAlias
from typing_extensions import TypeAliasType

from pydantic import BaseModel, Field, model_serializer

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
    params: StructuredType | None = None
    id: str | NumberType | None


JsonRpcBatchRequest = Annotated[list[JsonRpcRequest], Field(min_length=1)]


class JsonRpcResponse(BaseModel):
    jsonrpc: str
    id: str | NumberType | None


class JsonRpcSuccessResponse(JsonRpcResponse):
    result: JsonType


class JsonRpcErrorObject(BaseModel):
    code: int
    message: str
    data: JsonType = None

    @model_serializer
    def serialize(self, _info):
        out = {"code": self.code, "message": self.message}
        if self.data is not None:
            out["data"] = self.data
        return out


class JsonRpcErrorResponse(JsonRpcResponse):
    error: JsonRpcErrorObject
