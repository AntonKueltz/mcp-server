from http.client import OK
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from mcp_server.context import RequestContext
from mcp_server.lifecycle.methods import initialize
from tests import TestWithApp


class TestInitializeMethods(IsolatedAsyncioTestCase):
    async def test_initialize(self):
        client_protocol_version = "2025-03-26"
        context = RequestContext(AsyncMock(), AsyncMock())
        actual, _ = await initialize(client_protocol_version, {}, {}, context)

        self.assertEqual(actual["protocolVersion"], "2025-03-26")
        self.assertEqual(actual["capabilities"], {"prompts": {"listChanged": False}})


class TestInitializeMethodsFunctional(TestWithApp):
    async def test_initialize(self):
        protocol_version = "2025-06-18"
        init_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": protocol_version,
                "capabilities": {},
                "clientInfo": {},
            },
        }

        resp = self.client.post("/", json=init_body)
        self.assertEqual(resp.status_code, OK)

        data = resp.json()
        self.assertEqual(data["result"]["protocolVersion"], protocol_version)

        headers = resp.headers
        self.assertIsNotNone(headers["mcp-session-id"])
