from fastapi import APIRouter

from json_rpc_server.methods import Methods
from json_rpc_server.model import (
    INVALID_PARAMS,
    JsonRpcRequest,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
    METHOD_NOT_FOUND,
)

router = APIRouter()


@router.post("/")
async def handle_post_json_rpc_request(
    body: JsonRpcRequest,
) -> JsonRpcErrorResponse | JsonRpcSuccessResponse:
    if not hasattr(Methods, body.method):
        return JsonRpcErrorResponse(
            jsonrpc=body.jsonrpc,
            id=body.jsonrpc,
            error=JsonRpcErrorObject(
                code=METHOD_NOT_FOUND,
                message=f"{body.method} is not a known method",
                data=None,
            ),
        )

    result = None
    try:
        if isinstance(body.params, list):
            result = getattr(Methods, body.method)(*body.params)
        elif isinstance(body.params, dict):
            result = getattr(Methods, body.method)(**body.params)

    except TypeError:
        return JsonRpcErrorResponse(
            jsonrpc=body.jsonrpc,
            id=body.jsonrpc,
            error=JsonRpcErrorObject(
                code=INVALID_PARAMS,
                message=f"{body.params} are not valid parameters for {body.method}",
                data=None,
            ),
        )

    return JsonRpcSuccessResponse(
        jsonrpc=body.jsonrpc,
        id=body.id,
        result=result,
    )
