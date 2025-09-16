from unittest import TestCase

from mcp_server.lifecycle.methods import initialize


class TestInitializeMethods(TestCase):
    def test_initialize(self):
        client_protocol_version = "2025-03-26"
        actual, _ = initialize(client_protocol_version, {}, {})

        self.assertEqual(actual["protocolVersion"], "2025-03-26")
        self.assertEqual(actual["capabilities"], {})
