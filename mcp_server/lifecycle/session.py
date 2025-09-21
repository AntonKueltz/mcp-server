from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha3_256
from hmac import compare_digest, digest
from typing import Any
from uuid import uuid4

from redis.asyncio.client import Redis

from mcp_server.context import mcp_session_id_var


# define this interface so we can mock out redis with a lightweight map in tests
class StoreProvider(ABC):
    @abstractmethod
    async def set(self, session_id: str, key: str, value: str):
        pass

    @abstractmethod
    async def get(self, session_id: str, key: str) -> str | None:
        pass

    @abstractmethod
    async def delete(self, session_id: str):
        pass


class RedisStore(StoreProvider):
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, session_id: str, key: str, value: str):
        await self.redis.hset(session_id, key, value)

    async def get(self, session_id: str, key: str) -> str | None:
        return await self.redis.hget(session_id, key)

    async def delete(self, session_id: str):
        await self.redis.delete(session_id)


class SessionStore:
    client: StoreProvider
    delimiter: str = "|"
    secret_key: bytes = b"very-secret-key!"

    def __init__(self, client: StoreProvider):
        self.client = client

    async def assign_session(self):
        _uuid = uuid4().bytes
        _hmac = digest(self.secret_key, _uuid, sha3_256)
        session_id = (
            f"{b64encode(_uuid).decode()}{self.delimiter}{b64encode(_hmac).decode()}"
        )

        await self.client.set(session_id, "created", str(datetime.now()))
        return session_id

    def validate_session_id(self, session_id: str | None) -> bool:
        if session_id is None:
            return False

        try:
            [_uuid, _hmac] = session_id.split(self.delimiter)
        except (AttributeError, ValueError):
            return False

        expected = b64decode(_hmac)
        computed = digest(self.secret_key, b64decode(_uuid), sha3_256)

        return compare_digest(expected, computed)

    async def get_session_data(self, key: str) -> str | None:
        session_id = mcp_session_id_var.get()

        if not self.validate_session_id(session_id):
            return None

        return await self.client.get(session_id, key)

    async def set_session_data(self, key: str, data: Any) -> bool:
        session_id = mcp_session_id_var.get()

        if not self.validate_session_id(session_id):
            return False

        await self.client.set(session_id, key, data)
        return True

    async def terminate_session(self, session_id: str) -> bool:
        if not self.validate_session_id(session_id):
            return False

        await self.client.delete(session_id)
        return True
