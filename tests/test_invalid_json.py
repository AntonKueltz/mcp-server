from unittest import TestCase

from fastapi.testclient import TestClient
from parameterized import parameterized

from json_rpc_server.main import app


class TestInvalidJson(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @parameterized.expand(
        [
            (
                '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]',
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None,
                },
            ),
            (
                """[
  {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
  {"jsonrpc": "2.0", "method"
]""",
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None,
                },
            ),
        ]
    )
    def test_invalid_json(self, input: str, expected: dict):
        resp = self.client.post(
            "/", content=input, headers={"Content-Type": "application/json"}
        )
        actual = resp.json()
        self.assertEqual(actual, expected)
