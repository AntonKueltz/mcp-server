from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    NO_CONTENT,
    OK,
    PARTIAL_CONTENT,
    UNAUTHORIZED,
)
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, Request
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


def _set_session(session_id: str | None):
    from mcp_server.main import app

    if session_id and not app.state.session_store.validate_session_id(session_id):
        raise HTTPException(status_code=UNAUTHORIZED)

    mcp_session_id_var.set(session_id)


@router.post("/")
async def json_rpc_request(
    body: list[Any] | dict,
    background_tasks: BackgroundTasks,
    mcp_session_id: str | None = Header(None),
):
    _set_session(mcp_session_id)

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
async def open_sse_stream(request: Request, mcp_session_id: str | None = Header(None)):
    from mcp_server.main import app

    _set_session(mcp_session_id)
    await app.state.session_store.set_session_data("has-event-stream", "1")

    async def stream_generator():
        while True:
            if await request.is_disconnected():
                break

            event = await app.state.event_queue.poll_event(timeout=1.0)
            print(event)
            if event and await app.state.event_queue.is_terminate_session_event(event):
                await request.close()
                break
            elif event:
                yield event

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.delete("/")
async def terminate_session(mcp_session_id: str | None = Header(None)):
    from mcp_server.main import app

    if mcp_session_id is None:
        return Response(status_code=BAD_REQUEST)

    _set_session(mcp_session_id)

    if await app.state.session_store.get_session_data("has-event-stream"):
        await app.state.event_queue.terminate_session(mcp_session_id)
    await app.state.session_store.terminate_session(mcp_session_id)

    return Response(status_code=NO_CONTENT)
