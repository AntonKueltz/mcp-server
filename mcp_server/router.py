from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    NO_CONTENT,
    OK,
    PARTIAL_CONTENT,
    UNAUTHORIZED,
)
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse
from functools import reduce

from mcp_server.context import RequestContext, get_event_queue, get_session_store
from mcp_server.json_rpc.handler import error_response, handle_single_request
from mcp_server.json_rpc.model import (
    INVALID_REQUEST,
    JsonRpcErrorResponse,
    JsonRpcSuccessResponse,
)
from mcp_server.lifecycle.session import SessionStore
from mcp_server.sse.queue import EventQueue

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


@router.post("/")
async def json_rpc_request(
    body: list[Any] | dict,
    background_tasks: BackgroundTasks,
    mcp_session_id: str | None = Header(None),
    event_queue: EventQueue = Depends(get_event_queue),
    session_store: SessionStore = Depends(get_session_store),
):
    if mcp_session_id and not session_store.validate_session_id(mcp_session_id):
        raise HTTPException(status_code=UNAUTHORIZED)

    request_context = RequestContext(event_queue, session_store, mcp_session_id)

    if isinstance(body, list):
        if body:
            result = [
                await handle_single_request(req, background_tasks, request_context)
                for req in body
            ]
            return _build_bulk_response(result)
        else:
            result = await error_response(INVALID_REQUEST, "Invalid Request")
            return _build_response(result, {})

    else:
        result = await handle_single_request(body, background_tasks, request_context)
        return _build_response(*result)


@router.get("/")
async def open_sse_stream(
    request: Request,
    mcp_session_id: str | None = Header(None),
    event_queue: EventQueue = Depends(get_event_queue),
    session_store: SessionStore = Depends(get_session_store),
):
    if mcp_session_id is None or not session_store.validate_session_id(mcp_session_id):
        raise HTTPException(status_code=UNAUTHORIZED)

    await session_store.set_session_data(mcp_session_id, "has-event-stream", "1")

    async def stream_generator():
        yield ": stream open\n\n"

        while True:
            if await request.is_disconnected():
                break

            event = await event_queue.poll_event(mcp_session_id, timeout=1.0)

            if event and event_queue.is_terminate_session_event(event):
                yield ": stream closed\n\n"
                await request.close()
                break

            elif event:
                yield event

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.delete("/")
async def terminate_session(
    mcp_session_id: str | None = Header(None),
    event_queue: EventQueue = Depends(get_event_queue),
    session_store: SessionStore = Depends(get_session_store),
):
    if mcp_session_id is None:
        return Response(status_code=BAD_REQUEST)
    if not session_store.validate_session_id(mcp_session_id):
        raise HTTPException(status_code=UNAUTHORIZED)

    if await session_store.get_session_data(mcp_session_id, "has-event-stream"):
        await event_queue.terminate_session(mcp_session_id)
    await session_store.terminate_session(mcp_session_id)

    return Response(status_code=NO_CONTENT)
