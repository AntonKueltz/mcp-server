from asyncio import QueueFull
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from mcp_server.sse.model import ServerSentEvent
from mcp_server.sse.producer import event_producer


class TestSSE_Producer(IsolatedAsyncioTestCase):
    async def test_enqueue_and_poll(self):
        event1 = ServerSentEvent(data="event1")
        event2 = ServerSentEvent(data="event2")

        self.assertTrue(await event_producer.enqueue_event(event1))
        self.assertTrue(await event_producer.enqueue_event(event2))

        dequeued1 = await event_producer.poll_event(timeout=0.01)
        dequeued2 = await event_producer.poll_event(timeout=0.01)

        self.assertEqual(dequeued1, event1)
        self.assertEqual(dequeued2, event2)

    async def test_queue_full(self):
        with patch.object(
            event_producer.queue, "put", new=AsyncMock(side_effect=QueueFull)
        ):
            self.assertFalse(await event_producer.enqueue_event(ServerSentEvent()))

    async def test_timeout(self):
        self.assertIsNone(await event_producer.poll_event(timeout=0.001))
