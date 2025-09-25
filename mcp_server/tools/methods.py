from typing import Any

from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult
from mcp_server.json_rpc.exceptions import JsonRpcException
from mcp_server.tools import all_tools, call_tool as call_tool_by_name


async def list_tools(request_context: RequestContext) -> MethodResult:
    tools = [t.as_list_item().model_dump() for t in all_tools.values()]
    return {"tools": tools}, {}


async def call_tool(
    name: str, arguments: dict[str, Any], request_context: RequestContext
) -> MethodResult:
    try:
        content = await call_tool_by_name(name, **arguments)
        result = {"content": [content.model_dump()], "isError": False}
    except JsonRpcException as exc:
        raise exc
    except Exception:
        result = {"content": [], "isError": True}

    return result, {}
