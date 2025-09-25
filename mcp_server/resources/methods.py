from pydantic import AnyUrl

from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.json_rpc.exceptions import JsonRpcException
from mcp_server.json_rpc.model import INVALID_PARAMS
from mcp_server.resources import all_resources, get_resource


async def list_resources(request_context: RequestContext) -> MethodResult:
    resources = {
        "resources": [r.as_list_item().model_dump() for r in all_resources.values()]
    }
    return resources, {}


async def read_resource(uri: str, request_context: RequestContext) -> MethodResult:
    url = AnyUrl(uri)
    resource = get_resource(url)

    if resource is None:
        raise JsonRpcException(code=INVALID_PARAMS, message="Resource not found")

    content = await resource.get_content()
    return {"contents": [resource.as_detail(content).model_dump()]}, {}
