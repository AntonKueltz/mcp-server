from http.client import NOT_FOUND

from fastapi import HTTPException
from pydantic import AnyUrl

from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.resources.inventory import all_resources, get_resource


async def list_resources(request_context: RequestContext) -> MethodResult:
    resources = {
        "resources": [r.as_list_item().model_dump() for r in all_resources.values()]
    }
    return resources, {}


async def read_resource(uri: str, request_context: RequestContext) -> MethodResult:
    resource = get_resource(AnyUrl(uri))

    if resource is None:
        raise HTTPException(status_code=NOT_FOUND)

    return {"contents": [resource.as_detail().model_dump()]}, {}
