from http.client import ACCEPTED, BAD_REQUEST, OK, PARTIAL_CONTENT
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from mcp_server.json_rpc.handler import error_response, handle_single_request
from mcp_server.json_rpc.model import (
    INVALID_REQUEST,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)

router = APIRouter()


def _build_response(
    result: JsonRpcErrorResponse
    | JsonRpcSuccessResponse
    | None
    | list[JsonRpcErrorResponse | JsonRpcSuccessResponse | None],
) -> Response:
    if not result or (isinstance(result, list) and all([not r for r in result])):
        return Response(status_code=ACCEPTED)

    if isinstance(result, list):
        filtered: list[JsonRpcErrorResponse | JsonRpcSuccessResponse] = [
            r for r in result if r is not None
        ]

        if all([isinstance(r, JsonRpcSuccessResponse) for r in filtered]):
            status_code = OK
        elif all([isinstance(r, JsonRpcErrorResponse) for r in filtered]):
            status_code = BAD_REQUEST
        else:
            status_code = PARTIAL_CONTENT

        return JSONResponse(
            status_code=status_code, content=[r.model_dump() for r in filtered]
        )

    elif isinstance(result, JsonRpcSuccessResponse):
        return JSONResponse(status_code=OK, content=result.model_dump())

    elif isinstance(result, JsonRpcErrorResponse):
        return JSONResponse(status_code=BAD_REQUEST, content=result.model_dump())


@router.post("/")
async def handle_post_json_rpc_request(
    body: list[Any] | dict, background_tasks: BackgroundTasks
):
    if isinstance(body, list):
        if body:
            result = [
                await handle_single_request(req, background_tasks) for req in body
            ]
            return _build_response(result)
        else:
            result = await error_response(INVALID_REQUEST, "Invalid Request")
            return _build_response(result)

    else:
        result = await handle_single_request(body, background_tasks)
        return _build_response(result)


@router.get("/")
async def handle_open_sse_stream(request: Request):
    from mcp_server.sse.producer import event_producer

    async def stream_generator():
        while True:
            if await request.is_disconnected():
                break

            event = await event_producer.poll_event(timeout=1.0)
            if event:
                yield event.serialize()
            else:
                yield ": keep-alive\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
