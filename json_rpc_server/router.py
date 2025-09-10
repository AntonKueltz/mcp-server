from fastapi import APIRouter

from json_rpc_server.methods import Methods
from json_rpc_server.model import (
    INVALID_PARAMS,
    JsonRpcRequest,
    JsonRpcBatchRequest,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
    METHOD_NOT_FOUND,
)

router = APIRouter()


async def _handle_single_request(
    body: JsonRpcRequest,
) -> JsonRpcErrorResponse | JsonRpcSuccessResponse:
    if not hasattr(Methods, body.method):
        return JsonRpcErrorResponse(
            jsonrpc=body.jsonrpc,
            id=body.id,
            error=JsonRpcErrorObject(
                code=METHOD_NOT_FOUND,
                message="Method not found",
            ),
        )

    try:
        if isinstance(body.params, list):
            result = getattr(Methods, body.method)(*body.params)
        elif isinstance(body.params, dict):
            result = getattr(Methods, body.method)(**body.params)
        else:
            result = getattr(Methods, body.method)()

    except TypeError:
        return JsonRpcErrorResponse(
            jsonrpc=body.jsonrpc,
            id=body.id,
            error=JsonRpcErrorObject(
                code=INVALID_PARAMS,
                message=f"{body.params} are not valid parameters for {body.method}",
            ),
        )

    return JsonRpcSuccessResponse(
        jsonrpc=body.jsonrpc,
        id=body.id,
        result=result,
    )


@router.post("/")
async def handle_post_json_rpc_request(
    body: JsonRpcRequest | JsonRpcBatchRequest,
) -> (
    JsonRpcErrorResponse
    | JsonRpcSuccessResponse
    | list[JsonRpcErrorResponse | JsonRpcSuccessResponse]
):
    if isinstance(body, list):
        return [await _handle_single_request(req) for req in body]
    else:
        return await _handle_single_request(body)
