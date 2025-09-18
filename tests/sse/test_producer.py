from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from redis.exceptions import ConnectionError, TimeoutError

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

        self.assertEqual(dequeued1, event1.serialize())
        self.assertEqual(dequeued2, event2.serialize())

    async def test_no_data_in_event(self):
        self.assertFalse(await event_producer.enqueue_event(ServerSentEvent()))

    async def test_queue_unavailable(self):
        with patch.object(
            event_producer.redis_client,
            "rpush",
            new=AsyncMock(side_effect=ConnectionError),
        ):
            self.assertFalse(
                await event_producer.enqueue_event(ServerSentEvent(data="{}"))
            )

    async def test_queue_timeout(self):
        with patch.object(
            event_producer.redis_client,
            "blpop",
            new=AsyncMock(side_effect=TimeoutError),
        ):
            self.assertIsNone(await event_producer.poll_event(timeout=0.001))
