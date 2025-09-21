from contextlib import asynccontextmanager
from http.client import BAD_REQUEST

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.asyncio.client import Redis

from mcp_server.json_rpc.model import (
    PARSE_ERROR,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
)
from mcp_server.sse.queue import EventQueue, RedisQueue
from mcp_server.lifecycle.session import RedisStore, SessionStore
from mcp_server.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis()
    app.state.session_store = SessionStore(RedisStore(redis))
    app.state.event_queue = EventQueue(RedisQueue(redis))

    try:
        yield
    finally:
        await redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def invalid_request_handler(_, __):
    error = JsonRpcErrorResponse(
        jsonrpc="2.0",
        id=None,
        error=JsonRpcErrorObject(
            code=PARSE_ERROR,
            message="Parse error",
        ),
    )

    return JSONResponse(status_code=BAD_REQUEST, content=error.model_dump())
