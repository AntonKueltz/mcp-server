from http.client import OK
from unittest.mock import patch

from mcp_server.resources import add_resource
from mcp_server.resources.model import Resource, TextContent
from tests import TestWithApp

file_contents = TextContent(
    mime_type="text/x-rust",
    text='fn main() {\n    println!("Hello world!");\n}',
)
resource = Resource(
    uri="file:///project/src/main.rs",
    name="main.rs",
    title="Rust Software Application Main File",
    description="Primary application entry point",
)

add_resource(resource)


class TestPromptMethods(TestWithApp):
    def test_list_resources(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "resources/list"}
        expected = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "resources": [
                    {
                        "uri": "file:///project/src/main.rs",
                        "name": "main.rs",
                        "title": "Rust Software Application Main File",
                        "description": "Primary application entry point",
                        "mimeType": "text/x-rust",
                    }
                ],
            },
        }

        with patch(
            "mcp_server.resources.file_system.read_file", return_value=file_contents
        ):
            resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_read_resource(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": "file:///project/src/main.rs"},
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "contents": [
                    {
                        "uri": "file:///project/src/main.rs",
                        "name": "main.rs",
                        "title": "Rust Software Application Main File",
                        "mimeType": "text/x-rust",
                        "text": 'fn main() {\n    println!("Hello world!");\n}',
                    }
                ]
            },
        }

        with patch(
            "mcp_server.resources.file_system.read_file", return_value=file_contents
        ):
            resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)
