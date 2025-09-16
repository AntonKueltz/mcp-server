from http.client import ACCEPTED, BAD_REQUEST, NO_CONTENT, OK
from unittest import TestCase

from fastapi.testclient import TestClient
from parameterized import parameterized

from mcp_server.main import app
from mcp_server.lifecycle.session import SessionStore


class TestLifecycleSession(TestCase):
    def test_assign_and_validate_session(self):
        store = SessionStore()
        session_id = store.assign_session()
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
        store = SessionStore()
        self.assertFalse(store.validate_session_id(session_id))

    def test_assign_and_terminate_session(self):
        store = SessionStore()
        session_id = store.assign_session()

        self.assertTrue(store.terminate_session(session_id))
        self.assertNotIn(session_id, store.mapping)


class TestLifecycleSessionFunctional(TestCase):
    def setUp(self):
        self.session_header = "mcp-session-id"
        self.client = TestClient(app)
        self.init_request_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {},
            },
        }
        self.init_notification_body = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }

    def test_terminate_missing_header(self):
        # missing header is an explicit error status code
        resp = self.client.delete("/")
        self.assertEqual(resp.status_code, BAD_REQUEST)

        # invalid session data is not
        resp = self.client.delete("/", headers={self.session_header: "foobar"})
        self.assertEqual(resp.status_code, NO_CONTENT)

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
