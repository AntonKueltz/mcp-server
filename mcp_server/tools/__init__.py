from functools import wraps
from typing import Any, Awaitable, Callable

from mcp_server.json_rpc.exceptions import JsonRpcException
from mcp_server.json_rpc.model import INVALID_PARAMS
from mcp_server.model import Content
from mcp_server.tools.model import Tool

all_tools: dict[str, Tool] = {}


async def call_tool(name: str, *args, **kwargs) -> Content:
    if name not in all_tools:
        raise JsonRpcException(code=INVALID_PARAMS, message=f"Unknown tool: {name}")

    tool = all_tools[name]
    return await tool.callable(*args, **kwargs)


def tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    title: str | None = None,
    output_schema: dict[str, Any] | None = None,
):
    def decorator(func: Callable[..., Awaitable[Content]]):
        t = Tool(
            name=name,
            title=title,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            callable=func,
        )
        all_tools[name] = t

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
