from unittest import TestCase

from fastapi.testclient import TestClient
from parameterized import parameterized

from json_rpc_server.main import app


class TestBatch(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @parameterized.expand(
        [
            (
                [
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [42, 23],
                        "id": 1,
                    },
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [10, 2],
                        "id": 2,
                    },
                ],
                [
                    {"jsonrpc": "2.0", "result": 19, "id": 1},
                    {"jsonrpc": "2.0", "result": 8, "id": 2},
                ],
            ),
            (
                [
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [42],
                        "id": 1,
                    },
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [10, 2],
                        "id": 2,
                    },
                ],
                [
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": {"params": [42]},
                        },
                        "id": 1,
                    },
                    {"jsonrpc": "2.0", "result": 8, "id": 2},
                ],
            ),
            (
                [
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [42, 23],
                        "id": 1,
                    },
                    [],
                    {
                        "jsonrpc": "2.0",
                        "method": "subtract",
                        "params": [10, 2],
                        "id": 2,
                    },
                    {"jsonrpc": "2.0", "method": "does_not_exist", "id": "1"},
                ],
                [
                    {"jsonrpc": "2.0", "result": 19, "id": 1},
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    },
                    {"jsonrpc": "2.0", "result": 8, "id": 2},
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": "Method not found",
                            "data": {"method": "does_not_exist"},
                        },
                        "id": "1",
                    },
                ],
            ),
        ]
    )
    def test_batch(self, input: dict, expected: dict):
        resp = self.client.post("/", json=input)
        actual = resp.json()
        self.assertEqual(actual, expected)
