from functools import wraps
from typing import Awaitable, Callable

from mcp_server.prompts.model import Argument, Message, Prompt

all_prompts: dict[str, Prompt] = {}


def get_prompt(name: str) -> Prompt | None:
    return all_prompts.get(name)


def prompt(
    name: str,
    title: str | None = None,
    description: str | None = None,
    arguments: list[Argument] | None = None,
):
    def decorator(func: Callable[..., Awaitable[list[Message]]]):
        p = Prompt(
            name=name,
            title=title,
            description=description,
            arguments=arguments,
            set_messages=func,
        )
        all_prompts[name] = p

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
