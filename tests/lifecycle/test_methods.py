from unittest import IsolatedAsyncioTestCase

from mcp_server.lifecycle.methods import initialize


class TestInitializeMethods(IsolatedAsyncioTestCase):
    async def test_initialize(self):
        client_protocol_version = "2025-03-26"
        actual, _ = await initialize(client_protocol_version, {}, {})

        self.assertEqual(actual["protocolVersion"], "2025-03-26")
        self.assertEqual(actual["capabilities"], {})
