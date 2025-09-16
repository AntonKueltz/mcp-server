# Overview
A server implementing the Model Context Protocol (MCP). This code is pre-alpha.

The goals of this implementation are -
* Minimal third party dependencies (fastapi and a handful of test tools for dev)
* Extensibility
* Feature richness
* Ease of development (i.e. a well organized codebase and an implementation that attempts to be minimal without being too clever)

# Organization
TODO

# Development

### Prerequisites
* uv - `pip install uv`

### Run Server

    uv run fastapi dev mcp_server/main.py

### Run Tests

    uv run pytest
