from typing import Any

from fastapi import BackgroundTasks
from pydantic import ValidationError

from mcp_server.context import meta_progress_token_var
from mcp_server.data_types import MethodResult
from mcp_server.methods import registry
from mcp_server.json_rpc.model import (
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcRequest,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)


async def error_response(
    code: int, message: str, request: JsonRpcRequest | None = None
) -> JsonRpcErrorResponse:
    data = None

    if request:
        if code == INVALID_PARAMS:
            data = {"params": request.params}
        elif code == METHOD_NOT_FOUND:
            data = {"method": request.method}

    return JsonRpcErrorResponse(
        jsonrpc=request.jsonrpc if request else "2.0",
        id=request.id if request else None,
        error=JsonRpcErrorObject(
            code=code,
            message=message,
            data=data,
        ),
    )


async def _call_method(json_rpc_request: JsonRpcRequest) -> MethodResult:
    if isinstance(json_rpc_request.params, list):
        return await registry[json_rpc_request.method](*json_rpc_request.params)
    elif isinstance(json_rpc_request.params, dict):
        return await registry[json_rpc_request.method](**json_rpc_request.params)
    else:
        return await registry[json_rpc_request.method]()


def _set_progress_token(request: JsonRpcRequest):
    if isinstance(request.params, dict):
        _meta = request.params.get("_meta")

        if isinstance(_meta, dict):
            token = _meta.get("progressToken")
            meta_progress_token_var.set(token)

        if _meta is not None:
            del request.params["_meta"]


async def handle_single_request(
    body: Any,
    background_tasks: BackgroundTasks,
) -> tuple[JsonRpcErrorResponse | JsonRpcSuccessResponse | None, dict]:
    try:
        json_rpc_request = JsonRpcRequest.model_validate(body)
    except ValidationError:
        return await error_response(INVALID_REQUEST, "Invalid Request"), {}

    _set_progress_token(json_rpc_request)

    if json_rpc_request.method not in registry:
        return await error_response(
            METHOD_NOT_FOUND, "Method not found", json_rpc_request
        ), {}

    try:
        # handle notifications which do not expect a response
        if json_rpc_request.id is None:
            background_tasks.add_task(_call_method, json_rpc_request)
            return None, {}

        result, headers = await _call_method(json_rpc_request)
    except TypeError:
        return await error_response(
            INVALID_PARAMS, "Invalid params", json_rpc_request
        ), {}

    return (
        JsonRpcSuccessResponse(
            jsonrpc=json_rpc_request.jsonrpc,
            id=json_rpc_request.id,
            result=result,
        ),
        headers,
    )
