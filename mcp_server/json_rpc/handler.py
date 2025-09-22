from dataclasses import replace
from typing import Any

from fastapi import BackgroundTasks
from pydantic import ValidationError

from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.json_rpc.model import (
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    JsonRpcRequest,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)
from mcp_server.methods import registry


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


async def _call_method(
    json_rpc_request: JsonRpcRequest, request_context: RequestContext
) -> MethodResult:
    if isinstance(json_rpc_request.params, list):
        args = json_rpc_request.params + [request_context]
        return await registry[json_rpc_request.method](*args)

    elif isinstance(json_rpc_request.params, dict):
        kwargs = json_rpc_request.params | {"request_context": request_context}
        return await registry[json_rpc_request.method](**kwargs)

    else:
        return await registry[json_rpc_request.method](request_context)


def _get_progress_token(request: JsonRpcRequest) -> str | int | None:
    if isinstance(request.params, dict):
        _meta = request.params.get("_meta")

        token = None
        if isinstance(_meta, dict):
            token = _meta.get("progressToken")

        if _meta is not None:
            del request.params["_meta"]

        return token


async def handle_single_request(
    body: Any,
    background_tasks: BackgroundTasks,
    request_context: RequestContext,
) -> tuple[JsonRpcErrorResponse | JsonRpcSuccessResponse | None, dict]:
    try:
        json_rpc_request = JsonRpcRequest.model_validate(body)
    except ValidationError:
        return await error_response(INVALID_REQUEST, "Invalid Request"), {}

    token = _get_progress_token(json_rpc_request)
    updated_context = replace(request_context, progress_token=token)

    if json_rpc_request.method not in registry:
        return await error_response(
            METHOD_NOT_FOUND, "Method not found", json_rpc_request
        ), {}

    try:
        # handle notifications which do not expect a response
        if json_rpc_request.id is None:
            background_tasks.add_task(_call_method, json_rpc_request, updated_context)
            return None, {}

        result, headers = await _call_method(json_rpc_request, updated_context)
    except TypeError as e:
        print(e)
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
