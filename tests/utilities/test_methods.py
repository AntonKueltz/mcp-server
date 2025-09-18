from http.client import OK
from unittest import TestCase

from fastapi.testclient import TestClient

from mcp_server.main import app


class TestUtilitiesMethods(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ping(self):
        request_body = {"jsonrpc": "2.0", "id": "123", "method": "ping"}
        expected = {"jsonrpc": "2.0", "id": "123", "result": {}}

        resp = self.client.post("/", json=request_body)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)
