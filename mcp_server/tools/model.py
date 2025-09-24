from typing import Any, Awaitable, Callable

from mcp_server.model import BaseConfig, Content


class ToolListItem(BaseConfig):
    name: str
    title: str | None = None
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


class Tool(BaseConfig):
    name: str
    title: str | None = None
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    callable: Callable[..., Awaitable[Content]]

    def as_list_item(self) -> ToolListItem:
        return ToolListItem(
            name=self.name,
            title=self.title,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
        )
