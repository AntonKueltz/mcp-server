from abc import ABC, abstractmethod
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
