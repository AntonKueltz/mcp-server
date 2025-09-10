from fastapi import FastAPI

from json_rpc_server.router import router

app = FastAPI()
app.include_router(router)
