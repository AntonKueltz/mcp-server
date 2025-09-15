from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class SubCapabilities(BaseConfig):
    list_changed: bool | None = None
    subscribe: bool | None = None


class ClientCapabilities(BaseConfig):
    roots: SubCapabilities | None = None
    sampling: SubCapabilities | None = None
    experimental: SubCapabilities | None = None


class ServerCapabilities(BaseConfig):
    prompts: SubCapabilities | None = None
    resources: SubCapabilities | None = None
    tools: SubCapabilities | None = None
    logging: SubCapabilities | None = None
    completions: SubCapabilities | None = None
    experimental: SubCapabilities | None = None
