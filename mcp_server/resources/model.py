from datetime import datetime
from typing import Awaitable, Callable

from pydantic import AnyUrl

from mcp_server.model import BaseConfig, Role


class Annotation(BaseConfig):
    audience: list[Role] | None = None
    priority: float | None = None
    last_modified: datetime | None = None


class TextContent(BaseConfig):
    text: str


class BinaryContent(BaseConfig):
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
    mime_type: str
    annotations: Annotation | None = None
    get_content: Callable[[], Awaitable[BinaryContent | TextContent]]

    def as_list_item(self) -> ResourceListItem:
        return ResourceListItem(
            uri=self.uri,
            name=self.name,
            title=self.title,
            description=self.description,
            mime_type=self.mime_type,
            size=self.size,
        )

    def as_detail(self, content: BinaryContent | TextContent) -> ResourceDetail:
        if isinstance(content, TextContent):
            return ResourceDetail(
                uri=self.uri,
                name=self.name,
                title=self.title,
                mime_type=self.mime_type,
                text=content.text,
            )
        else:
            return ResourceDetail(
                uri=self.uri,
                name=self.name,
                title=self.title,
                mime_type=self.mime_type,
                blob=content.blob,
            )
