from asyncio import Queue
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from redis.exceptions import ConnectionError, TimeoutError

from mcp_server.sse.model import ServerSentEvent
from mcp_server.sse.queue import EventQueue, QueueProvider


class MockRedis(QueueProvider):
    q: Queue

    def __init__(self):
        self.q = Queue()

    async def push(self, key, data: str):
        await self.q.put(data.encode())

    async def pop(self, key, timeout):
        return 0, await self.q.get()

    async def close(self):
        pass


class TestSSE_Queue(IsolatedAsyncioTestCase):
    def setUp(self):
        # mock the redis client with a normal async queue
        self.queue = EventQueue(MockRedis())

    async def test_enqueue_and_poll(self):
        event1 = ServerSentEvent(data="event1")
        event2 = ServerSentEvent(data="event2")

        self.assertTrue(await self.queue.enqueue_event(event1))
        self.assertTrue(await self.queue.enqueue_event(event2))

        dequeued1 = await self.queue.poll_event(timeout=0.01)
        dequeued2 = await self.queue.poll_event(timeout=0.01)

        self.assertEqual(dequeued1, event1.serialize())
        self.assertEqual(dequeued2, event2.serialize())

    async def test_no_data_in_event(self):
        self.assertFalse(await self.queue.enqueue_event(ServerSentEvent()))

    async def test_queue_unavailable(self):
        self.queue.client.push = AsyncMock(side_effect=ConnectionError)
        self.assertFalse(await self.queue.enqueue_event(ServerSentEvent(data="{}")))

    async def test_queue_timeout(self):
        self.queue.client.pop = AsyncMock(side_effect=TimeoutError)
        self.assertIsNone(await self.queue.poll_event(timeout=0.001))
