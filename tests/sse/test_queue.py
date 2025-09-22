from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from redis.exceptions import ConnectionError, TimeoutError

from mcp_server.sse.model import ServerSentEvent
from mcp_server.sse.queue import EventQueue
from tests import InMemoryQueue


class TestSSE_Queue(IsolatedAsyncioTestCase):
    def setUp(self):
        # mock the redis client with a normal async queue
        self.queue = EventQueue(InMemoryQueue())

    async def test_enqueue_and_poll(self):
        session_id = "session"
        event1 = ServerSentEvent(data="event1")
        event2 = ServerSentEvent(data="event2")

        self.assertTrue(await self.queue.enqueue_event(session_id, event1))
        self.assertTrue(await self.queue.enqueue_event(session_id, event2))

        dequeued1 = await self.queue.poll_event(session_id, timeout=0.01)
        dequeued2 = await self.queue.poll_event(session_id, timeout=0.01)

        self.assertEqual(dequeued1, event1.serialize())
        self.assertEqual(dequeued2, event2.serialize())

    async def test_no_data_in_event(self):
        self.assertFalse(await self.queue.enqueue_event("session", ServerSentEvent()))

    async def test_queue_unavailable(self):
        self.queue.client.push = AsyncMock(side_effect=ConnectionError)
        self.assertFalse(
            await self.queue.enqueue_event("session", ServerSentEvent(data="{}"))
        )

    async def test_queue_timeout(self):
        self.queue.client.pop = AsyncMock(side_effect=TimeoutError)
        self.assertIsNone(await self.queue.poll_event("session", timeout=0.001))
