from http.client import ACCEPTED, BAD_REQUEST, NO_CONTENT, OK, UNAUTHORIZED
from unittest import IsolatedAsyncioTestCase

from parameterized import parameterized

from mcp_server.lifecycle.session import SessionStore
from tests import InMemoryStore, TestWithApp


class TestLifecycleSession(IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = SessionStore(InMemoryStore())

    async def test_assign_and_validate_session(self):
        session_id = await self.store.assign_session()
        self.assertTrue(self.store.validate_session_id(session_id))

    @parameterized.expand(
        [
            (None,),
            ("",),
            ("does-not-exist",),
            (""),
            ("bWNw|bWNw"),
        ]
    )
    async def test_terminate_invalid_session(self, session_id):
        self.assertFalse(await self.store.terminate_session(session_id))

    async def test_assign_and_terminate_session(self):
        session_id = await self.store.assign_session()

        self.assertTrue(await self.store.terminate_session(session_id))

    async def test_get_invalid_session(self):
        self.assertEqual(await self.store.get_session_data("session", "foobar"), None)

    async def test_set_invalid_session_data(self):
        self.assertFalse(await self.store.set_session_data("session", "key", "value"))


class TestLifecycleSessionFunctional(TestWithApp):
    def setUp(self):
        self.session_header = "mcp-session-id"
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
