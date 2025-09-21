from http.client import OK
from unittest import TestCase
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from mcp_server.lifecycle.session import SessionStore
from mcp_server.main import app
from mcp_server.methods import registry
from mcp_server.sse.client_notifications import progress_notification
from mcp_server.sse.queue import EventQueue


# define a simple method that reports progress and register it the service
async def method_with_progress_notification():
    await progress_notification(progress=50, total=100, message="Testing 123...")
    return {}, {}


registry["example"] = method_with_progress_notification


class TestUtilitiesMethods(TestCase):
    def setUp(self):
        redis = AsyncMock()
        app.state.session_store = SessionStore(redis)
        app.state.event_queue = EventQueue(redis)

        self.client = TestClient(app)

    def test_ping(self):
        request_body = {"jsonrpc": "2.0", "id": "123", "method": "ping"}
        expected = {"jsonrpc": "2.0", "id": "123", "result": {}}

        resp = self.client.post("/", json=request_body)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_progress(self):
        init_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {},
            },
        }

        # initialize a session
        resp = self.client.post("/", json=init_body)
        self.assertEqual(resp.status_code, OK)
        session_id = resp.headers["mcp-session-id"]
        headers = {"mcp-session-id": session_id}

        # open up an event stream for the session
        _ = self.client.stream("/", "GET", headers=headers)

        # call a method that reports progress to the event stream
        method_body = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "example",
            "params": {"_meta": {"progressToken": "example-token"}},
        }
        resp = self.client.post("/", json=method_body, headers=headers)
        self.assertEqual(resp.status_code, OK)
