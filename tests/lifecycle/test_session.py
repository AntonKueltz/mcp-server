from unittest import TestCase

from mcp_server.lifecycle.session import SessionStore


class TestLifecycleSession(TestCase):
    def test_assign_and_validate_session(self):
        store = SessionStore()
        session_id = store.assign_session()
        print(session_id)
        self.assertTrue(store.validate_session_id(session_id))
