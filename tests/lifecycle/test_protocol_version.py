from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from fastapi import HTTPException
from parameterized import parameterized

from mcp_server.context import RequestContext
from mcp_server.lifecycle.protocol_version import (
    ProtocolVersion,
    identify_protocol_version,
    negotiate_version,
)


class TestLifecycleProtocolVersion(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_context = RequestContext(
            AsyncMock(), AsyncMock(get_session_data=AsyncMock(return_value=None))
        )

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
        actual = await identify_protocol_version(headers, self.mock_context)
        self.assertEqual(actual, expected)

    async def test_invalid_identify_protocol_version(self):
        with self.assertRaises(HTTPException):
            await identify_protocol_version(
                {"mcp-protocol-version": "2024-11-05"}, self.mock_context
            )

    async def test_protocol_version_from_context(self):
        context = RequestContext(
            AsyncMock(),
            AsyncMock(get_session_data=AsyncMock(return_value="2025-06-18")),
        )

        actual = await identify_protocol_version({}, context)
        self.assertEqual(actual, ProtocolVersion.VERSION_2025_06_18)
