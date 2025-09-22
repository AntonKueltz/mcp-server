from mcp_server.context import RequestContext
from mcp_server.data_types import MethodResult, NumberType
from mcp_server.sse.client_notifications import progress_notification


async def ping(request_context: RequestContext | None = None) -> MethodResult:
    return {}, {}


async def cancelled_notification(
    request_id: str | NumberType,
    reason: str | None = None,
    request_context: RequestContext | None = None,
) -> MethodResult:
    return None, {}


async def long_running(request_context: RequestContext) -> MethodResult:
    from time import sleep

    result = 0

    for i in range(10):
        sleep(0.5)
        result += i
        await progress_notification(
            request_context=request_context,
            progress=(i + 1) * 10,
            total=100,
            message=f"partial result = {result}",
        )

    return {"sum": result}, {}
