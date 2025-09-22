from http.client import BAD_REQUEST

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from mcp_server.json_rpc.model import (
    PARSE_ERROR,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
)
from mcp_server.router import router

app = FastAPI()
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
