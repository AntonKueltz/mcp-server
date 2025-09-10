from json_rpc_server.model import NumberType


class Methods:
    @staticmethod
    def subtract(minuend: NumberType, subtrahend: NumberType) -> NumberType:
        return minuend - subtrahend
