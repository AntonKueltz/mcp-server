from http.client import NO_CONTENT, OK

from mcp_server.context import RequestContext
from mcp_server.methods import registry
from mcp_server.sse.client_notifications import progress_notification
from tests import TestWithApp


# define a simple method that reports progress and register it the service
async def method_with_progress_notification(request_context: RequestContext):
    await progress_notification(
        request_context, progress=50, total=100, message="Testing 123..."
    )
    return {}, {}


registry["example"] = method_with_progress_notification


class TestUtilitiesMethods(TestWithApp):
    def test_ping(self):
        request_body = {"jsonrpc": "2.0", "id": "123", "method": "ping"}
        expected = {"jsonrpc": "2.0", "id": "123", "result": {}}

        resp = self.client.post("/", json=request_body)

        self.assertEqual(resp.status_code, OK)
        self.assertEqual(resp.json(), expected)

    def test_progress(self):
        init_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {},
            },
        }

        # initialize a session
        resp = self.client.post("/", json=init_body)
        self.assertEqual(resp.status_code, OK)
        session_id = resp.headers["mcp-session-id"]
        headers = {"mcp-session-id": session_id}

        # open up an event stream for the session
        _ = self.client.stream("GET", "/", headers=headers)

        # call a method that reports progress to the event stream
        method_body = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "example",
            "params": {"_meta": {"progressToken": "example-token"}},
        }
        resp = self.client.post("/", json=method_body, headers=headers)
        self.assertEqual(resp.status_code, OK)

        # events = []
        # for line in stream.iter_lines():
        #     if line.startswith("data:"):
        #         events.append(line)
        #     if line == "":
        #         break

        # close the stream and end the session
        resp = self.client.delete("/", headers=headers)
        self.assertEqual(resp.status_code, NO_CONTENT)

        # self.assertEqual(events, "foo")
