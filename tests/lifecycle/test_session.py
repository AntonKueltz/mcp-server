from http.client import ACCEPTED, BAD_REQUEST, NO_CONTENT, OK, UNAUTHORIZED
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from parameterized import parameterized

from mcp_server.main import app
from mcp_server.lifecycle.session import SessionStore
from mcp_server.sse.queue import EventQueue


class TestLifecycleSession(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.redis = AsyncMock()

    async def test_assign_and_validate_session(self):
        store = SessionStore(self.redis)
        session_id = await store.assign_session()
        self.assertTrue(store.validate_session_id(session_id))

    @parameterized.expand(
        [
            (None,),
            ("",),
            ("does-not-exist",),
            (""),
            ("bWNw|bWNw"),
        ]
    )
    def test_terminate_invalid_session(self, session_id):
        store = SessionStore(self.redis)
        self.assertFalse(store.validate_session_id(session_id))

    async def test_assign_and_terminate_session(self):
        store = SessionStore(self.redis)
        session_id = await store.assign_session()

        self.assertTrue(await store.terminate_session(session_id))

    async def test_get_invalid_session(self):
        store = SessionStore(self.redis)
        self.assertEqual(await store.get_session_data("foobar"), None)

    async def test_set_invalid_session_data(self):
        store = SessionStore(self.redis)
        self.assertFalse(await store.set_session_data("key", "value"))


class TestLifecycleSessionFunctional(TestCase):
    def setUp(self):
        self.session_header = "mcp-session-id"
        self.client = TestClient(app)
        self.init_request_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {},
            },
        }
        self.init_notification_body = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }

        self.redis = AsyncMock()
        app.state.session_store = SessionStore(self.redis)
        app.state.event_queue = EventQueue(self.redis)

    def tearDown(self):
        app.state.session_store = None
        app.state.event_queue = None

    def test_terminate_invalid_header(self):
        resp = self.client.delete("/")
        self.assertEqual(resp.status_code, BAD_REQUEST)

        resp = self.client.delete("/", headers={self.session_header: "session-123"})
        self.assertEqual(resp.status_code, UNAUTHORIZED)

    def test_assign_and_terminate_session(self):
        resp = self.client.post("/", json=self.init_request_body)
        self.assertEqual(resp.status_code, OK)

        session_id = resp.headers[self.session_header]
        resp = self.client.delete("/", headers={self.session_header: session_id})
        self.assertEqual(resp.status_code, NO_CONTENT)

    def test_initalization_flow(self):
        resp = self.client.post("/", json=self.init_request_body)
        self.assertEqual(resp.status_code, OK)

        session_id = resp.headers[self.session_header]

        resp = self.client.post(
            "/",
            json=self.init_notification_body,
            headers={self.session_header: session_id},
        )
        self.assertEqual(resp.status_code, ACCEPTED)
