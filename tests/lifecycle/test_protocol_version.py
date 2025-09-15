from unittest import TestCase

from parameterized import parameterized

from mcp_server.lifecycle.protocol_version import ProtocolVersion, negotiate_version


class TestLifecycleProtocolVersion(TestCase):
    @parameterized.expand(
        [
            ("2024-11-05", ProtocolVersion.VERSION_2024_11_05),
            ("2025-03-26", ProtocolVersion.VERSION_2025_03_26),
            ("2025-06-18", ProtocolVersion.VERSION_2025_06_18),
            ("2000-01-01", ProtocolVersion.VERSION_2025_06_18),
            (1, ProtocolVersion.VERSION_2025_06_18),
            (None, ProtocolVersion.VERSION_2025_06_18),
        ]
    )
    def test_negotiate_version(self, client_version, expected):
        actual = negotiate_version(client_version)
        self.assertEqual(actual, expected)
