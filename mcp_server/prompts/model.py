from abc import ABC, abstractmethod
from enum import Enum

from pydantic import AnyUrl, FileUrl

from mcp_server.model import BaseConfig


class Argument(BaseConfig):
    name: str
    description: str
    required: bool


class PromptListItem(BaseConfig):
    name: str
    title: str | None = None
    description: str | None = None
    arguments: list[Argument] | None = None


class TextContent(BaseConfig):
    type: str = "text"
    text: str


class ImageContent(BaseConfig):
    type: str = "image"
    data: str
    mime_type: str


class AudioContent(BaseConfig):
    type: str = "audio"
    data: str
    mime_type: str


class Resource(BaseConfig):
    uri: AnyUrl | FileUrl
    name: str
    title: str
    mime_type: str
    text: str


class EmbeddedResource(BaseConfig):
    type: str = "resource"
    resource: Resource


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseConfig):
    role: Role
    content: TextContent | ImageContent | AudioContent | EmbeddedResource


class PromptDetail(BaseConfig):
    description: str | None
    messages: list[Message]


class Prompt(BaseConfig, ABC):
    name: str
    messages: list[Message]
    title: str | None = None
    description: str | None = None
    arguments: list[Argument] | None = None

    def as_list_item(self) -> PromptListItem:
        return PromptListItem(
            name=self.name,
            title=self.title,
            description=self.description,
            arguments=self.arguments,
        )

    def as_detail(self) -> PromptDetail:
        return PromptDetail(description=self.description, messages=self.messages)

    @abstractmethod
    def set_messages(self, arguments: dict[str, str] | None):
        pass
