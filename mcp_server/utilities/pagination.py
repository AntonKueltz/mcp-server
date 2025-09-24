from base64 import b64decode, b64encode
from dataclasses import dataclass, asdict
from json import dumps, loads

PAGE_SIZE = 10


@dataclass
class Cursor:
    start: int
    end: int


def parse_cursor(cursor: str) -> tuple[int, int]:
    serialized = b64decode(cursor).decode()
    parsed = Cursor(**loads(serialized))
    return parsed.start, parsed.end


def create_next_cursor(prev_cursor: str | None) -> str:
    if prev_cursor is None:
        start, end = PAGE_SIZE, 2 * PAGE_SIZE
    else:
        _, prev_end = parse_cursor(prev_cursor)
        start, end = prev_end, prev_end + PAGE_SIZE

    cursor = Cursor(start=start, end=end)
    serialized = dumps(asdict(cursor))
    return b64encode(serialized.encode()).decode()
