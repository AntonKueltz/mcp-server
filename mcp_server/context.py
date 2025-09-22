from dataclasses import dataclass

from redis.asyncio.client import Redis

from mcp_server.lifecycle.session import RedisStore, SessionStore
from mcp_server.sse.queue import EventQueue, RedisQueue


@dataclass
class RequestContext:
    event_queue: EventQueue
    session_store: SessionStore
    session_id: str | None = None
    progress_token: str | int | None = None


async def get_event_queue():
    redis = Redis()
    event_queue = EventQueue(RedisQueue(redis))

    try:
        yield event_queue
    finally:
        await redis.aclose()


async def get_session_store():
    redis = Redis()
    session_store = SessionStore(RedisStore(redis))

    try:
        yield session_store
    finally:
        await redis.aclose()
