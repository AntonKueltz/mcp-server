from http.client import NO_CONTENT
from unittest import TestCase

from fastapi.testclient import TestClient
from parameterized import parameterized

from json_rpc_server.main import app


class TestRfcExamples(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @parameterized.expand(
        [
            (
                {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1},
                {"jsonrpc": "2.0", "result": 19, "id": 1},
            ),
            (
                {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2},
                {"jsonrpc": "2.0", "result": -19, "id": 2},
            ),
            (
                {
                    "jsonrpc": "2.0",
                    "method": "subtract",
                    "params": {"subtrahend": 23, "minuend": 42},
                    "id": 3,
                },
                {"jsonrpc": "2.0", "result": 19, "id": 3},
            ),
            (
                {
                    "jsonrpc": "2.0",
                    "method": "subtract",
                    "params": {"minuend": 42, "subtrahend": 23},
                    "id": 4,
                },
                {"jsonrpc": "2.0", "result": 19, "id": 4},
            ),
            (
                {"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]},
                None,
            ),
            (
                {"jsonrpc": "2.0", "method": "foobar"},
                None,
            ),
            (
                {"jsonrpc": "2.0", "method": "does_not_exist", "id": "1"},
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": "1",
                },
            ),
            (
                {"jsonrpc": "2.0", "method": 1, "params": "bar"},
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None,
                },
            ),
            (
                [],
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None,
                },
            ),
            (
                [1],
                [
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    }
                ],
            ),
            (
                [1, 2, 3],
                [
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    },
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    },
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    },
                ],
            ),
            (
                [
                    {"jsonrpc": "2.0", "method": "notify_sum", "params": [1, 2, 4]},
                    {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
                ],
                None,
            ),
        ]
    )
    def test_examples(self, input: dict, expected: dict):
        print(input, expected)
        resp = self.client.post("/", json=input)
        actual = resp.json() if resp.status_code != NO_CONTENT else None
        self.assertEqual(actual, expected)
