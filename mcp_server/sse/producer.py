from redis.asyncio.client import Redis
from redis.exceptions import (
    ConnectionError,
    ResponseError,
    TimeoutError as RedisTimeout,
)

from mcp_server.context import mcp_session_id_var
from mcp_server.sse.model import ServerSentEvent


class EventProducerRedis:
    redis_client: Redis

    def __init__(self):
        self.redis_client = Redis()

    def _get_key(self) -> str:
        session_id = mcp_session_id_var.get()
        if session_id is None:
            return "events"

        return f"events:{session_id}"

    async def enqueue_event(self, event: ServerSentEvent) -> bool:
        try:
            key = self._get_key()
            await self.redis_client.rpush(key, event.serialize())
            return True
        except (ConnectionError, RedisTimeout, ResponseError, ValueError):
            return False

    async def poll_event(self, timeout: float) -> str | None:
        try:
            key = self._get_key()
            _, event = await self.redis_client.blpop(key, timeout=timeout)
            return event.decode()
        except (ConnectionError, RedisTimeout, ResponseError, TypeError):
            return None


event_producer = EventProducerRedis()
