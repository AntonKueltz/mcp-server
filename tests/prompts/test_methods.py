from http.client import OK

from mcp_server.prompts import add_prompt
from mcp_server.prompts.model import Argument, Message, Prompt, Role, TextContent
from tests import TestWithApp


class CodeReviewPrompt(Prompt):
    def set_messages(self, arguments: dict[str, str] | None):
        if arguments is None:
            raise ValueError("Code review prompt must have a `code` argument")

        code = arguments.get("code")
        text = f"Please review this code:\n```{code}```"
        message = Message(role=Role.USER, content=TextContent(text=text))

        self.messages = [message]


code_review = CodeReviewPrompt(
    name="code_review",
    messages=[],
    title="Request Code Review",
    description="Asks the LLM to analyze code quality and suggest improvements",
    arguments=[Argument(name="code", description="The code to review", required=True)],
)
add_prompt(code_review)


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
