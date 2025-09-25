from functools import wraps
from typing import Awaitable, Callable

from pydantic import AnyUrl

from mcp_server.resources.model import Annotation, BinaryContent, Resource, TextContent

all_resources: dict[AnyUrl, Resource] = {}


def add_resource(resource: Resource):
    all_resources[resource.uri] = resource


def get_resource(uri: AnyUrl) -> Resource | None:
    return all_resources.get(uri)


def resource(
    uri: AnyUrl,
    name: str,
    mime_type: str,
    title: str | None = None,
    description: str | None = None,
    size: int | None = None,
    annotations: Annotation | None = None,
):
    def decorator(func: Callable[[], Awaitable[BinaryContent | TextContent]]):
        r = Resource(
            uri=uri,
            name=name,
            title=title,
            description=description,
            size=size,
            mime_type=mime_type,
            annotations=annotations,
            get_content=func,
        )
        all_resources[uri] = r

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
