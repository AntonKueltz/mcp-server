from json import dumps

from mcp_server.context import meta_progress_token_var
from mcp_server.sse.model import ServerSentEvent
from mcp_server.sse.producer import event_producer


async def _send_notification(method: str, params: dict):
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }

    event = ServerSentEvent(data=dumps(data, indent=2))
    await event_producer.enqueue_event(event)


async def progress_notification(
    progress: int | float, total: int | float | None = None, message: str | None = None
):
    progress_token = meta_progress_token_var.get()
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

    await _send_notification("notifications/progress", params)
