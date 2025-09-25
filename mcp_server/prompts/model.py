from abc import ABC
from typing import Awaitable, Any, Callable

from mcp_server.model import (
    AudioContent,
    BaseConfig,
    EmbeddedResource,
    ImageContent,
    Role,
    TextContent,
)


class Argument(BaseConfig):
    name: str
    description: str
    required: bool


class PromptListItem(BaseConfig):
    name: str
    title: str | None = None
    description: str | None = None
    arguments: list[Argument] | None = None


class Message(BaseConfig):
    role: Role
    content: TextContent | ImageContent | AudioContent | EmbeddedResource


class PromptDetail(BaseConfig):
    description: str | None
    messages: list[Message]


class Prompt(BaseConfig, ABC):
    name: str
    title: str | None = None
    description: str | None = None
    arguments: list[Argument] | None = None
    set_messages: Callable[..., Awaitable[list[Message]]]

    def as_list_item(self) -> PromptListItem:
        return PromptListItem(
            name=self.name,
            title=self.title,
            description=self.description,
            arguments=self.arguments,
        )

    async def as_detail(self, args: dict[str, Any]) -> PromptDetail:
        messages = await self.set_messages(**args)
        return PromptDetail(description=self.description, messages=messages)
