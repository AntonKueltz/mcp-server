from abc import ABC, abstractmethod

from redis.asyncio.client import Redis
from redis.exceptions import (
    ConnectionError,
    ResponseError,
    TimeoutError as RedisTimeout,
)

from mcp_server.context import mcp_session_id_var
from mcp_server.sse.model import ServerSentEvent

TERMINATE_SESSION_EVENT = "TERMINATE_SESSION"


# define this interface so we can mock out redis with a lightweight queue in tests
class QueueProvider(ABC):
    @abstractmethod
    async def push(self, key: str, data: str):
        pass

    @abstractmethod
    async def pop(self, key: str, timeout: float | None) -> tuple[int, bytes] | None:
        pass

    @abstractmethod
    async def close(self):
        pass


class RedisQueue(QueueProvider):
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def push(self, key: str, data: str):
        await self.redis.rpush(key, data)

    async def pop(self, key: str, timeout: float | None) -> tuple[int, bytes] | None:
        await self.redis.blpop(key, timeout)

    async def close(self):
        await self.redis.close()


class EventQueue:
    client: QueueProvider

    def __init__(self, client: QueueProvider):
        self.client = client

    def _get_key(self) -> str:
        session_id = mcp_session_id_var.get()
        if session_id is None:
            return "events"

        return f"events:{session_id}"

    async def enqueue_event(self, event: ServerSentEvent) -> bool:
        try:
            key = self._get_key()
            await self.client.push(key, event.serialize())
            return True
        except (ConnectionError, RedisTimeout, ResponseError, ValueError):
            return False

    async def poll_event(self, timeout: float | None = None) -> str | None:
        try:
            key = self._get_key()
            _, event = await self.client.pop(key, timeout=timeout)
            return event.decode()
        except (ConnectionError, RedisTimeout, ResponseError, TypeError):
            return None

    async def terminate_session(self, mcp_session_id: str) -> bool:
        if mcp_session_id is None:
            raise ValueError("Cannot terminate a session with no session id")

        event = ServerSentEvent(event=TERMINATE_SESSION_EVENT)
        return await self.enqueue_event(event)

    async def is_terminate_session_event(self, event: str) -> bool:
        event = event.strip()
        return event == f"event: {TERMINATE_SESSION_EVENT}"
