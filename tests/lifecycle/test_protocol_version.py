from unittest import TestCase

from fastapi import HTTPException
from fastapi.testclient import TestClient
from parameterized import parameterized

from mcp_server.lifecycle.protocol_version import (
    ProtocolVersion,
    identify_protocol_version,
    negotiate_version,
)
from mcp_server.main import app


class TestLifecycleProtocolVersion(TestCase):
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
    def test_identify_protocol_version(self, headers, expected):
        actual = identify_protocol_version(headers)
        self.assertEqual(actual, expected)

    def test_invalid_identify_protocol_version(self):
        with self.assertRaises(HTTPException):
            identify_protocol_version({"mcp-protocol-version": "2024-11-05"})


class TestLifecycleProtocolVersionFunctional(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_session_defined_protocol_version(self):
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
        actual = identify_protocol_version(resp.headers)

        self.assertEqual(actual, ProtocolVersion.VERSION_2025_06_18)
