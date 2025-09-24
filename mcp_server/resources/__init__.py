from pydantic import AnyUrl

from mcp_server.resources.model import Resource

all_resources: dict[AnyUrl, Resource] = {}


def add_resource(resource: Resource):
    all_resources[resource.uri] = resource


def get_resource(uri: AnyUrl) -> Resource | None:
    return all_resources.get(uri)
