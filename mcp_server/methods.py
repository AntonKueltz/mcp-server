from typing import Callable

from mcp_server.lifecycle.methods import initialize, initialized_notification

registry: dict[str, Callable] = {
    "initialize": initialize,
    "notifications/initialized": initialized_notification,
}
