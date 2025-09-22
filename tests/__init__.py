from asyncio import Queue
from typing import Any
from unittest import IsolatedAsyncioTestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp_server.context import get_event_queue, get_session_store
from mcp_server.lifecycle.session import SessionStore, StoreProvider
from mcp_server.router import router
from mcp_server.sse.queue import EventQueue, QueueProvider

# persist in-memory data structures across requests
q: Queue = Queue()
d: dict[str, dict[str, Any]] = {}


class InMemoryQueue(QueueProvider):
    async def push(self, key, data: str):
        await q.put(data.encode())

    async def pop(self, key, timeout):
        return 0, await q.get()

    async def close(self):
        pass


class InMemoryStore(StoreProvider):
    async def set(self, session_id: str, key: str, value: str):
        if session_id in d:
            d[session_id][key] = value
        else:
            d[session_id] = {key: value}

    async def get(self, session_id: str, key: str) -> str | None:
        return d.get(session_id, {}).get(key)

    async def delete(self, session_id: str):
        del d[session_id]


# use this class to substitute e.g. redis with simpler in-memory data structures
class TestWithApp(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = InMemoryQueue()
        cls.store = InMemoryStore()

        async def override_get_event_queue():
            yield EventQueue(InMemoryQueue())

        async def override_get_session_store():
            yield SessionStore(InMemoryStore())

        cls.app = FastAPI()
        cls.app.include_router(router)

        cls.app.dependency_overrides[get_event_queue] = override_get_event_queue
        cls.app.dependency_overrides[get_session_store] = override_get_session_store

        cls.client = TestClient(cls.app)
