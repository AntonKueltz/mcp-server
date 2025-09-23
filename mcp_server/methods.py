from typing import Awaitable, Callable

from mcp_server.data_types import MethodResult
from mcp_server.lifecycle.methods import initialize, initialized_notification
from mcp_server.prompts.methods import get_prompt, list_prompts
from mcp_server.utilities.methods import cancelled_notification, ping, long_running

registry: dict[str, Callable[..., Awaitable[MethodResult]]] = {
    "initialize": initialize,
    "ping": ping,
    "prompts/get": get_prompt,
    "prompts/list": list_prompts,
    "notifications/cancelled": cancelled_notification,
    "notifications/initialized": initialized_notification,
    "long": long_running,
}
