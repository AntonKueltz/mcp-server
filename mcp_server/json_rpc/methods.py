from typing import Callable

from mcp_server.json_rpc.model import NumberType
from mcp_server.lifecycle.methods import initialize, initialized_notification


def subtract(minuend: NumberType, subtrahend: NumberType) -> NumberType:
    return minuend - subtrahend


def update(*args, **kwargs):
    print(f"Updating with params args {args} and kwargs {kwargs}")


def foobar():
    print("foobar!")


registry: dict[str, Callable] = {
    "initialize": initialize,
    "notifications/initialized": initialized_notification,
    "subtract": subtract,
    "update": update,
    "foobar": foobar,
}
