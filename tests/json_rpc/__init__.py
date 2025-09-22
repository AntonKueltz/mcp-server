from mcp_server.methods import registry


async def subtract(minuend, subtrahend, request_context):
    return minuend - subtrahend, {}


async def update(*args, **kwargs):
    print(f"Updating with params args {args} and kwargs {kwargs}")
    return None, {}


async def foobar(request_context):
    print("foobar!")
    return None, {}


registry["subtract"] = subtract
registry["update"] = update
registry["foobar"] = foobar
