from json import loads
from unittest import TestCase

from mcp_server.lifecycle.model import (
    ClientCapabilities,
    ServerCapabilities,
    SubCapabilities,
)


class TestLifecycleModel(TestCase):
    def test_parse_client_capabilities(self):
        raw_capabilities = """{
            "roots": {
                "listChanged": true
            },
            "sampling": {}
        }"""
        capabilities = loads(raw_capabilities)

        parsed = ClientCapabilities.model_validate(capabilities)

        self.assertIsNotNone(parsed.roots)
        self.assertTrue(parsed.roots.list_changed)
        self.assertIsNone(parsed.roots.subscribe)
        self.assertIsNotNone(parsed.sampling)
        self.assertIsNone(parsed.sampling.list_changed)
        self.assertIsNone(parsed.sampling.subscribe)
        self.assertIsNone(parsed.experimental)

    def test_dump_server_capabilities(self):
        expected = {
            "logging": {},
            "prompts": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "tools": {"listChanged": True},
        }
        server_model = ServerCapabilities(
            logging=SubCapabilities(),
            prompts=SubCapabilities(list_changed=True),
            resources=SubCapabilities(subscribe=True, list_changed=True),
            tools=SubCapabilities(list_changed=True),
        )

        actual = server_model.model_dump()

        self.assertEqual(actual, expected)
