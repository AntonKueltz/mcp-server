from unittest import TestCase

from parameterized import parameterized

from mcp_server.sse.model import ServerSentEvent


class TestSSE_Model(TestCase):
    @parameterized.expand(
        [
            (
                ServerSentEvent(data="This is the first message."),
                "data: This is the first message.\n\n",
            ),
            (
                ServerSentEvent(data="This is the second message, it\nhas two lines."),
                "data: This is the second message, it\ndata: has two lines.\n\n",
            ),
            (
                ServerSentEvent(event="add", data="73857293"),
                "event: add\ndata: 73857293\n\n",
            ),
        ]
    )
    def test_serialize(self, event: ServerSentEvent, expected: str):
        self.assertEqual(event.serialize(), expected)

    def test_serialize_empty(self):
        event = ServerSentEvent()

        with self.assertRaises(ValueError):
            event.serialize()
