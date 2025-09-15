from mcp_server.json_rpc.model import NumberType


class Methods:
    @staticmethod
    def subtract(minuend: NumberType, subtrahend: NumberType) -> NumberType:
        return minuend - subtrahend

    @staticmethod
    def update(*args, **kwargs):
        print(f"Updating with params args {args} and kwargs {kwargs}")

    @staticmethod
    def foobar():
        print("foobar!")
