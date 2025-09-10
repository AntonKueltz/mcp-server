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
        ]
    )
    def test_examples(self, input: dict, expected: dict):
        print(input, expected)
        resp = self.client.post("/", json=input)
        actual = resp.json()
        self.assertEqual(actual, expected)
