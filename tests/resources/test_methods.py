from http.client import OK

from pydantic import AnyUrl

from mcp_server.resources import resource
from mcp_server.resources.model import TextContent
from tests import TestWithApp

uri = AnyUrl("file:///project/src/main.rs")


@resource(
    uri=uri,
    name="main.rs",
    mime_type="text/x-rust",
    title="Rust Software Application Main File",
    description="Primary application entry point",
)
async def get_main_rs() -> TextContent:
    return TextContent(
        text='fn main() {\n    println!("Hello world!");\n}',
    )


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

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)
