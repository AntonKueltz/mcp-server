# Overview
A server implementing the Model Context Protocol (MCP). This code is pre-alpha.

The goals of this implementation are -
* Minimal third party dependencies (fastapi, redis, and a handful of test tools for dev)
* Extensibility
* Feature richness
* Ease of development (i.e. a well organized codebase and an implementation that attempts to be minimal without being too clever)

# Organization
TODO

# Development

### Prerequisites
* uv - `pip install uv`
* redis - [install](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/)

A redis server should be available for the application to use. By default the
application will try to connect to the default redis URI `redis://localhost:6379`.

### Run Server
For general development that does not require any coordination across requests

    uv run fastapi dev mcp_server/main.py

For development where you have multiple connections that need to coordinate (e.g.
you have an event stream open and want to test sending progress updates to it as
part of handling another request)

    uv run fastapi run --workers 2 mcp_server/main.py

### Run Tests

    uv run pytest
