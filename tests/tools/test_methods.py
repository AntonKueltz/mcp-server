from http.client import OK

from mcp_server.model import TextContent
from mcp_server.tools import tool
from tests import TestWithApp


@tool(
    name="get_weather",
    title="Weather Information Provider",
    description="Get current weather information for a location",
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name or zip code"}
        },
        "required": ["location"],
    },
)
async def get_weather(location: str) -> TextContent:
    text = (
        f"Current weather in {location}:\nTemperature: 72°F\nConditions: Partly cloudy"
    )
    return TextContent(text=text)


class TestToolMethods(TestWithApp):
    def test_list_tools(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": "get_weather",
                        "title": "Weather Information Provider",
                        "description": "Get current weather information for a location",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City name or zip code",
                                }
                            },
                            "required": ["location"],
                        },
                    }
                ],
            },
        }

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_call_tool(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_weather", "arguments": {"location": "New York"}},
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Current weather in New York:\nTemperature: 72°F\nConditions: Partly cloudy",
                    }
                ],
                "isError": False,
            },
        }

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_call_tool_invalid_arguments(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_weather", "arguments": {"foo": "bar"}},
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {"content": [], "isError": True},
        }

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)
