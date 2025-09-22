from json import dumps

from mcp_server.context import RequestContext
from mcp_server.sse.model import ServerSentEvent


async def progress_notification(
    request_context: RequestContext,
    progress: int | float,
    total: int | float | None = None,
    message: str | None = None,
):
    progress_token = request_context.progress_token
    if progress_token is None:
        return

    params = {
        "progressToken": progress_token,
        "progress": progress,
    }
    if total:
        params["total"] = total
    if message:
        params["message"] = message

    data = {
        "jsonrpc": "2.0",
        "method": "notifications/progress",
        "params": params,
    }

    event = ServerSentEvent(data=dumps(data, indent=2))
    await request_context.event_queue.enqueue_event(request_context.session_id, event)
