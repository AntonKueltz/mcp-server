from datetime import datetime
from enum import Enum

from pydantic import AnyUrl

from mcp_server.model import BaseConfig


class IntendedAudience(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Annotation(BaseConfig):
    audience: list[IntendedAudience]
    priority: float
    last_modified: datetime


class TextContent(BaseConfig):
    mime_type: str
    text: str


class BinaryContent(BaseConfig):
    mime_type: str
    blob: str


class ResourceListItem(BaseConfig):
    uri: AnyUrl
    name: str
    title: str | None = None
    description: str | None = None
    mime_type: str | None = None
    size: int | None = None


class ResourceDetail(BaseConfig):
    uri: AnyUrl
    name: str
    title: str | None = None
    mime_type: str | None = None
    text: str | None = None
    blob: str | None = None


class Resource(BaseConfig):
    uri: AnyUrl
    name: str
    content: TextContent | BinaryContent
    title: str | None = None
    description: str | None = None
    size: int | None = None

    def as_list_item(self) -> ResourceListItem:
        return ResourceListItem(
            uri=self.uri,
            name=self.name,
            title=self.title,
            description=self.description,
            mime_type=self.content.mime_type,
            size=self.size,
        )

    def as_detail(self) -> ResourceDetail:
        if isinstance(self.content, TextContent):
            return ResourceDetail(
                uri=self.uri,
                name=self.name,
                title=self.title,
                mime_type=self.content.mime_type,
                text=self.content.text,
            )
        else:
            return ResourceDetail(
                uri=self.uri,
                name=self.name,
                title=self.title,
                mime_type=self.content.mime_type,
                blob=self.content.blob,
            )
