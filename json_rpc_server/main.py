from http.client import BAD_REQUEST

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from json_rpc_server.model import (
    INVALID_REQUEST,
    JsonRpcErrorObject,
    JsonRpcErrorResponse,
)
from json_rpc_server.router import router

app = FastAPI()
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def invalid_request_handler(_, exc: RequestValidationError):
    response = JsonRpcErrorResponse(
        jsonrpc="2.0" if not hasattr(exc.body, "jsonrpc") else exc.body.jsonrpc,
        id=None if not hasattr(exc.body, "id") else exc.body.id,
        error=JsonRpcErrorObject(
            code=INVALID_REQUEST,
            message="Invalid Request",
        ),
    )

    return JSONResponse(status_code=BAD_REQUEST, content=response.model_dump())
