from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from fastapi import HTTPException
from fastapi.testclient import TestClient
from parameterized import parameterized

from mcp_server.context import mcp_session_id_var
from mcp_server.lifecycle.protocol_version import (
    ProtocolVersion,
    identify_protocol_version,
    negotiate_version,
)
from mcp_server.lifecycle.session import SessionStore
from mcp_server.main import app


class TestLifecycleProtocolVersion(IsolatedAsyncioTestCase):
    @parameterized.expand(
        [
            ("2024-11-05", ProtocolVersion.VERSION_2025_06_18),
            ("2025-03-26", ProtocolVersion.VERSION_2025_03_26),
            ("2025-06-18", ProtocolVersion.VERSION_2025_06_18),
            (1, ProtocolVersion.VERSION_2025_06_18),
            (None, ProtocolVersion.VERSION_2025_06_18),
        ]
    )
    def test_negotiate_version(self, client_version, expected):
        actual = negotiate_version(client_version)
        self.assertEqual(actual, expected)

    @parameterized.expand(
        [
            ({}, ProtocolVersion.VERSION_2025_03_26),
            (
                {"mcp-protocol-version": "2025-06-18"},
                ProtocolVersion.VERSION_2025_06_18,
            ),
            (
                {"mcp-protocol-version": "2025-03-26"},
                ProtocolVersion.VERSION_2025_03_26,
            ),
        ]
    )
    async def test_identify_protocol_version(self, headers, expected):
        app.state.session_store = AsyncMock(
            get_session_data=AsyncMock(return_value=None)
        )

        actual = await identify_protocol_version(headers)
        self.assertEqual(actual, expected)

        app.state.session_store = None

    async def test_invalid_identify_protocol_version(self):
        with self.assertRaises(HTTPException):
            await identify_protocol_version({"mcp-protocol-version": "2024-11-05"})


class TestLifecycleProtocolVersionFunctional(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

        redis = AsyncMock(get=AsyncMock(return_value="2025-06-18"))
        app.state.session_store = SessionStore(redis)

    def tearDown(self) -> None:
        app.state.session_store = None

    async def test_session_defined_protocol_version(self):
        init_request_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {},
            },
        }

        resp = self.client.post("/", json=init_request_body)
        mcp_session_id_var.set(resp.headers.get("mcp-session-id"))
        actual = await identify_protocol_version(headers={})

        self.assertEqual(actual, ProtocolVersion.VERSION_2025_06_18)
