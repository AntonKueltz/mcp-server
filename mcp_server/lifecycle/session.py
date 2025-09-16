from base64 import b64decode, b64encode
from hashlib import sha3_256
from hmac import compare_digest, digest
from secrets import token_bytes
from typing import Any
from uuid import uuid4


class SessionStore:
    delimiter: str = "|"
    secret_key: bytes
    mapping: dict[str, Any]

    def __init__(self):
        self.secret_key = token_bytes(32)
        self.mapping = {}

    def assign_session(self):
        _uuid = uuid4().bytes
        _hmac = digest(self.secret_key, _uuid, sha3_256)
        session_id = (
            f"{b64encode(_uuid).decode()}{self.delimiter}{b64encode(_hmac).decode()}"
        )

        self.mapping[session_id] = {}
        return session_id

    def validate_session_id(self, session_id: str) -> bool:
        try:
            [_uuid, _hmac] = session_id.split(self.delimiter)
        except (AttributeError, ValueError):
            return False

        expected = b64decode(_hmac)
        computed = digest(self.secret_key, b64decode(_uuid), sha3_256)

        return compare_digest(expected, computed)

    def terminate_session(self, session_id: str) -> bool:
        if not self.validate_session_id(session_id):
            return False

        del self.mapping[session_id]
        return True


session_store = SessionStore()
