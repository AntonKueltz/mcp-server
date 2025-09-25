from http.client import BAD_REQUEST, OK

from mcp_server.prompts import prompt
from mcp_server.prompts.model import Argument, Message, Role, TextContent
from tests import TestWithApp


@prompt(
    name="code_review",
    title="Request Code Review",
    description="Asks the LLM to analyze code quality and suggest improvements",
    arguments=[Argument(name="code", description="The code to review", required=True)],
)
async def code_review(code: str) -> list[Message]:
    text = f"Please review this code:\n```{code}```"
    message = Message(role=Role.USER, content=TextContent(text=text))
    return [message]


class TestPromptMethods(TestWithApp):
    def test_list_prompts(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/list",
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "prompts": [
                    {
                        "name": "code_review",
                        "title": "Request Code Review",
                        "description": "Asks the LLM to analyze code quality and suggest improvements",
                        "arguments": [
                            {
                                "name": "code",
                                "description": "The code to review",
                                "required": True,
                            }
                        ],
                    }
                ],
            },
        }

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_get_prompt(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/get",
            "params": {
                "name": "code_review",
                "arguments": {"code": "def hello():\n    print('world')"},
            },
        }
        expected = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "description": "Asks the LLM to analyze code quality and suggest improvements",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": "Please review this code:\n```def hello():\n    print('world')```",
                        },
                    }
                ],
            },
        }

        resp = self.client.post("/", json=req)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_get_prompt_invalid_name(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/get",
            "params": {
                "name": "does_not_exist",
                "arguments": {},
            },
        }

        resp = self.client.post("/", json=req)
        self.assertEqual(resp.status_code, BAD_REQUEST)

        error = resp.json()["error"]
        self.assertEqual(error["code"], -32602)
        self.assertEqual(error["message"], "Invalid prompt name: does_not_exist")

    def test_get_prompt_invalid_args(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/get",
            "params": {
                "name": "code_review",
                "arguments": {},
            },
        }

        resp = self.client.post("/", json=req)
        self.assertEqual(resp.status_code, BAD_REQUEST)

        error = resp.json()["error"]
        self.assertEqual(error["code"], -32602)
        self.assertEqual(error["message"], "Missing required argument: code")
