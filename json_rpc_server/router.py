from http.client import BAD_REQUEST, OK, PARTIAL_CONTENT
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from json_rpc_server.handler import error_response, handle_single_request
from json_rpc_server.model import (
    INVALID_REQUEST,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)

router = APIRouter()


def _determine_status_code(
    result: JsonRpcErrorResponse
    | JsonRpcSuccessResponse
    | list[JsonRpcErrorResponse | JsonRpcSuccessResponse],
) -> int:
    if not isinstance(result, list):
        result = [result]

    if all([isinstance(r, JsonRpcSuccessResponse) for r in result]):
        return OK
    elif all([isinstance(r, JsonRpcErrorResponse) for r in result]):
        return BAD_REQUEST
    else:
        return PARTIAL_CONTENT


@router.post("/")
async def handle_post_json_rpc_request(body: list[Any] | dict):
    if isinstance(body, list):
        if body:
            results = [await handle_single_request(req) for req in body]
            status_code = _determine_status_code(results)
            return JSONResponse(
                status_code=status_code, content=[r.model_dump() for r in results]
            )
        else:
            result = await error_response(INVALID_REQUEST, "Invalid Request")
            return JSONResponse(status_code=BAD_REQUEST, content=result.model_dump())

    else:
        result = await handle_single_request(body)
        status_code = _determine_status_code(result)
        return JSONResponse(status_code=status_code, content=result.model_dump())
