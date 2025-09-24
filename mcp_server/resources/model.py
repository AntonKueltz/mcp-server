from datetime import datetime
from enum import Enum

from pydantic import AnyUrl, computed_field

from mcp_server.model import BaseConfig


class IntendedAudience(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Annotation(BaseConfig):
    audience: list[IntendedAudience] | None = None
    priority: float | None = None
    last_modified: datetime | None = None


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
    annotations: Annotation | None = None


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
    title: str | None = None
    description: str | None = None
    size: int | None = None
    annotations: Annotation | None = None

    @computed_field
    @property
    def content(self) -> TextContent | BinaryContent:
        from mcp_server.resources.file_system import read_file

        if self.uri.scheme == "file":
            return read_file(self.uri)

        raise ValueError("Unsupported URI scheme")

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
