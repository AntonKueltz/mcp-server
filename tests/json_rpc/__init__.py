from mcp_server.methods import registry


def subtract(minuend, subtrahend):
    return minuend - subtrahend, {}


def update(*args, **kwargs):
    print(f"Updating with params args {args} and kwargs {kwargs}")
    return None, {}


def foobar():
    print("foobar!")
    return None, {}


registry["subtract"] = subtract
registry["update"] = update
registry["foobar"] = foobar
