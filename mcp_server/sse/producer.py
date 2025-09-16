from asyncio import Queue, QueueFull, TimeoutError, wait_for

from mcp_server.sse.model import ServerSentEvent


class EventProducer:
    queue: Queue

    def __init__(self):
        self.queue = Queue()

    async def enqueue_event(self, event: ServerSentEvent) -> bool:
        try:
            await self.queue.put(event)
            return True
        except QueueFull:
            return False

    async def poll_event(self, timeout: float = 0.1) -> ServerSentEvent | None:
        try:
            return await wait_for(self.queue.get(), timeout=timeout)
        except TimeoutError:
            return None


event_producer = EventProducer()
