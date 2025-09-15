from typing import Any

from fastapi import BackgroundTasks
from pydantic import ValidationError

from json_rpc_server.methods import Methods
from json_rpc_server.model import (
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


async def _call_method(json_rpc_request: JsonRpcRequest) -> Any:
    if isinstance(json_rpc_request.params, list):
        return getattr(Methods, json_rpc_request.method)(*json_rpc_request.params)
    elif isinstance(json_rpc_request.params, dict):
        return getattr(Methods, json_rpc_request.method)(**json_rpc_request.params)
    else:
        return getattr(Methods, json_rpc_request.method)()


async def handle_single_request(
    body: Any,
    background_tasks: BackgroundTasks,
) -> JsonRpcErrorResponse | JsonRpcSuccessResponse | None:
    try:
        json_rpc_request = JsonRpcRequest.model_validate(body)
    except ValidationError:
        return await error_response(INVALID_REQUEST, "Invalid Request")

    if not hasattr(Methods, json_rpc_request.method):
        return await error_response(
            METHOD_NOT_FOUND, "Method not found", json_rpc_request
        )

    try:
        # handle notifications which do not expect a response
        if json_rpc_request.id is None:
            background_tasks.add_task(_call_method, json_rpc_request)
            return None

        result = await _call_method(json_rpc_request)
    except TypeError:
        return await error_response(INVALID_PARAMS, "Invalid params", json_rpc_request)

    return JsonRpcSuccessResponse(
        jsonrpc=json_rpc_request.jsonrpc,
        id=json_rpc_request.id,
        result=result,
    )
