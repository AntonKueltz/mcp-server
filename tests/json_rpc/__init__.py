from mcp_server.json_rpc.methods import registry


def subtract(minuend, subtrahend):
    return minuend - subtrahend


def update(*args, **kwargs):
    print(f"Updating with params args {args} and kwargs {kwargs}")


def foobar():
    print("foobar!")


registry["subtract"] = subtract
registry["update"] = update
registry["foobar"] = foobar
