from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    NO_CONTENT,
    OK,
    PARTIAL_CONTENT,
    UNAUTHORIZED,
)
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse
from functools import reduce

from mcp_server.context import mcp_session_id_var
from mcp_server.json_rpc.handler import error_response, handle_single_request
from mcp_server.json_rpc.model import (
    INVALID_REQUEST,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)
from mcp_server.lifecycle.session import session_store

router = APIRouter()


def _build_bulk_response(
    result: list[tuple[JsonRpcErrorResponse | JsonRpcSuccessResponse | None, dict]],
) -> Response:
    if all([not r for (r, _) in result]):
        return Response(status_code=ACCEPTED)

    headers = reduce(
        lambda d1, d2: d1 | d2,
        (h for (r, h) in result if isinstance(r, JsonRpcSuccessResponse)),
        {},
    )
    filtered: list[JsonRpcErrorResponse | JsonRpcSuccessResponse] = [
        r for (r, _) in result if r is not None
    ]

    if all([isinstance(r, JsonRpcSuccessResponse) for r in filtered]):
        status_code = OK
    elif all([isinstance(r, JsonRpcErrorResponse) for r in filtered]):
        status_code = BAD_REQUEST
    else:
        status_code = PARTIAL_CONTENT

    return JSONResponse(
        status_code=status_code,
        content=[r.model_dump() for r in filtered],
        headers=headers,
    )


def _build_response(
    result: JsonRpcErrorResponse | JsonRpcSuccessResponse | None,
    headers: dict,
) -> Response:
    if result is None:
        return Response(status_code=ACCEPTED)

    elif isinstance(result, JsonRpcSuccessResponse):
        return JSONResponse(
            status_code=OK, content=result.model_dump(), headers=headers
        )

    elif isinstance(result, JsonRpcErrorResponse):
        return JSONResponse(status_code=BAD_REQUEST, content=result.model_dump())


def _set_session(request: Request):
    session_id = request.headers.get("mcp-session-id")

    if session_id and not session_store.validate_session_id(session_id):
        raise HTTPException(status_code=UNAUTHORIZED)

    mcp_session_id_var.set(session_id)


@router.post("/")
async def json_rpc_request(
    request: Request, body: list[Any] | dict, background_tasks: BackgroundTasks
):
    _set_session(request)

    if isinstance(body, list):
        if body:
            result = [
                await handle_single_request(req, background_tasks) for req in body
            ]
            return _build_bulk_response(result)
        else:
            result = await error_response(INVALID_REQUEST, "Invalid Request")
            return _build_response(result, {})

    else:
        result = await handle_single_request(body, background_tasks)
        return _build_response(*result)


@router.get("/")
async def open_sse_stream(request: Request):
    from mcp_server.sse.producer import event_producer

    _set_session(request)

    async def stream_generator():
        while True:
            if await request.is_disconnected():
                break

            event = await event_producer.poll_event(timeout=1.0)
            if event:
                yield event
            else:
                yield ": keep-alive\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.delete("/")
async def terminate_session(request: Request):
    if "mcp-session-id" not in request.headers:
        return Response(status_code=BAD_REQUEST)

    session_store.terminate_session(request.headers["mcp-session-id"])
    return Response(status_code=NO_CONTENT)
