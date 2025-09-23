from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)
