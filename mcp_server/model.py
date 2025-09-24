from enum import Enum

from pydantic import AnyUrl, BaseModel, ConfigDict, FileUrl
from pydantic.alias_generators import to_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        return super().model_dump(
            mode="json", by_alias=True, exclude_none=True, **kwargs
        )


class Content(BaseConfig):
    text: str


class TextContent(Content):
    type: str = "text"
    text: str


class ImageContent(Content):
    type: str = "image"
    data: str
    mime_type: str


class AudioContent(Content):
    type: str = "audio"
    data: str
    mime_type: str


class Resource(BaseConfig):
    uri: AnyUrl | FileUrl
    name: str
    title: str
    mime_type: str
    text: str


class EmbeddedResource(Content):
    type: str = "resource"
    resource: Resource


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
