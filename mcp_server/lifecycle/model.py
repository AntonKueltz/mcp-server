from mcp_server.model import BaseConfig


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
